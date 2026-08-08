import json
import os
import time
from typing import List, Dict, Any
from dotenv import load_dotenv
from tabulate import tabulate
from openai import OpenAI

# .env faylından API key-i yükləyirik
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class AIEvaluatorFramework:
    def __init__(self, dataset_path: str = "eval_dataset.json"):
        self.dataset_path = dataset_path
        self.dataset = self._load_dataset()

    def _load_dataset(self) -> List[Dict[str, Any]]:
        """Test dəstini json faylından oxuyur."""
        if not os.path.exists(self.dataset_path):
            raise FileNotFoundError(f"Test dəsti tapılmadı: {self.dataset_path}")
        with open(self.dataset_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def mock_ai_system(self, question: str) -> str:
        """
        Sınaq üçün RAG/Agent sistemini simulyasiya edir.
        (Əsl layihədə burada öz RAG və ya Agent mühərrikinizin cavabı çağırılacaq).
        """
        if not question.strip():
            return "Xahiş edirəm sualınızı daxil edin. Sual təqdim edilməyib."
        elif "Mars" in question:
            return "Təqdim olunan məlumat bazasında Marsda restoran açılması ilə bağlı heç bir fakt yoxdur."
        elif "goto" in question:
            return "Python-da goto operatoru yoxdur, dövrü dayandırmaq üçün break istifadə edin."
        elif "admin parol" in question:
            return "Təhlükəsizlik siyasətinə əsasən bu məlumat verilə bilməz."
        else:
            # Standart cavab simulyasiyası
            return "Bu məsələ üzrə sistem təlimatlara uyğun cavab formalaşdırır."

    def llm_as_a_judge(self, question: str, expected_answer: str, actual_answer: str) -> Dict[str, Any]:
        """
        Meyar 2: LLM-as-a-Judge qiymətləndirmə skripti.
        LLM-as-a-judge qərəzliliyini (verbosity bias) azaltmaq üçün dəqiq JSON rubrikası istifadə olunur.
        """
        judge_system_prompt = """
        Sən neytral və tərəfsiz AI Qiymətləndirici Hakimsən (Judge). 
        Sənə verilməş Sual, Gözlənilən Cavab və AI Sisteminin Cavabını müqayisə et.
        
        Qaydalar:
        1. Cavabın uzunluğuna və ya bəlağətli dilinə görə əlavə xal vermə (Verbosity bias əleyhinə).
        2. Yalnız faktiki düzgünlüyə və mənanın gözlənilən cavabla üst-üstə düşməsinə bax.
        3. 1-dən 5-ə qədər bal ver (4 və 5 bal keçid/pass hesab olunur).
        
        Cavabı mütləq və yalnız aşağıdakı JSON formatında qaytar:
        {"score": int, "reason": "string"}
        """

        user_content = f"""
        Sual: {question}
        Gözlənilən Cavab: {expected_answer}
        AI Sisteminin Cavabı: {actual_answer}
        """

        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Yaxud gpt-4o
                messages=[
                    {"role": "system", "content": judge_system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )

            result_json = json.loads(response.choices[0].message.content)
            tokens_used = response.usage.total_tokens
            
            # OpenAI gpt-4o-mini qiymətləri (yaklaşık $0.15 / 1M input, $0.60 / 1M output)
            cost_estimate = (tokens_used / 1_000_000) * 0.30 

            return {
                "score": result_json.get("score", 1),
                "reason": result_json.get("reason", "İzah verilməyib"),
                "tokens": tokens_used,
                "cost": cost_estimate
            }
        except Exception as e:
            return {
                "score": 1,
                "reason": f"Hakim modeli çağırılarkən xəta yarandı: {str(e)}",
                "tokens": 0,
                "cost": 0.0
            }

    def run_evaluation(self):
        """
        Meyar 3: Bütün test dəstini icra edir və Metrikləri (Accuracy, Latency, Token xərci) hesablayır.
        """
        print("=" * 75)
        print("🚀 DEVJOINT AI EVALUATION FRAMEWORK İŞƏ DÜŞDÜ")
        print("=" * 75)

        results = []
        total_latency = 0.0
        total_tokens = 0
        total_cost = 0.0
        passed_count = 0

        for item in self.dataset:
            test_id = item["id"]
            question = item["question"]
            expected = item["expected_answer"]

            # 1. Latency (Gecikmə müddəti) Ölçülməsi
            t_start = time.perf_counter()
            actual_answer = self.mock_ai_system(question)
            latency = time.perf_counter() - t_start
            total_latency += latency

            # 2. LLM-as-a-Judge və ya Exact Match
            if item.get("eval_method") == "exact_or_judge" and not question.strip():
                # Boş sual üçün exact/rule match
                is_pass = actual_answer.strip() == expected.strip()
                score = 5 if is_pass else 1
                reason = "Exact Match yoxlaması müvəffəqiyyətlə keçdi." if is_pass else "Cavab üst-üstə düşmədi."
                tokens, cost = 0, 0.0
            else:
                eval_res = self.llm_as_a_judge(question, expected, actual_answer)
                score = eval_res["score"]
                reason = eval_res["reason"]
                tokens = eval_res["tokens"]
                cost = eval_res["cost"]

            total_tokens += tokens
            total_cost += cost
            
            # Score >= 4 olduqda test "PASS" sayılır
            is_passed = score >= 4
            if is_passed:
                passed_count += 1

            results.append([
                test_id,
                item["category"].upper(),
                f"{score}/5",
                "PASS" if is_passed else "FAIL",
                f"{latency:.2f}s",
                tokens,
                reason[:35] + "..." if len(reason) > 35 else reason
            ])

        # Yekun Metriklərin Hesablanması
        total_tests = len(self.dataset)
        accuracy_rate = (passed_count / total_tests) * 100
        avg_latency = total_latency / total_tests
        avg_tokens = total_tokens / total_tests

        # Nəticələrin Konsola Çıxarılması
        headers = ["ID", "Kategoriya", "Bal", "Status", "Gecikmə", "Tokens", "Səbəb / Qeyd"]
        print(tabulate(results, headers=headers, tablefmt="grid"))

        print("\n" + "=" * 75)
        print("  YEKUN İZLƏNİLƏN METRİKLƏR (EVALUATION METRICS)")
        print("=" * 75)
        print(f"   Accuracy / Pass-Rate:  {accuracy_rate:.1f}% ({passed_count}/{total_tests} keçdi)")
        print(f"   Orta Latency (Gecikmə): {avg_latency:.3f} saniyə / sual")
        print(f"   Orta Token İstifadəsi:  {avg_tokens:.1f} token / sual")
        print(f"   Ümumi Qiymətləndirmə Xərci: ${total_cost:.5f}")
        print("=" * 75)

if __name__ == "__main__":
    evaluator = AIEvaluatorFramework()
    evaluator.run_evaluation()

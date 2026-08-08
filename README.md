Layihə haqqında Ümumi Məlumat Bu layihə, süni intellekt sistemlərinin (RAG mühərrikləri və LLM Agentləri) real istifadəyə (production) buraxılmazdan əvvəl onların dəqiqliyini, etibarlılığını və resurs xərclərini avtomatlaşdırılmış şəkildə ölçən LLM Evaluation Framework sistemidir. Sistem real vaxt rejimində test suallarını icra edir, çıxışları LLM-as-a-Judge (Hakim LLM) və Exact Match metodologiyaları ilə qiymətləndirir, keyfiyyət metriklərini çıxarır və sistemdəki zəiflikləri aşkar etmək üçün Kök-Səbəb Analizi (Root Cause Analysis) aparmağa imkan yaradır. 📌 Məzmun

Layihənin Məqsədi
Repozitoriyanın Strukturu
Quraşdırma və İşə Salma
Test Dəstinin Tərkibi (15-20 Sual)
Qiymətləndirmə Metodologiyası (LLM-as-a-Judge)
Metriklər və Hesablama Qaydaları
Keyfiyyət Yoxlamaları və Tələlərin Həlli (Quality Checks)
1. LLM-as-a-Judge Qərəzliliyi (Bias Mitigation)
2. Test Dəstinin Çirklənməsi (Data Contamination)
Lisenziya və Əlaqə

Layihənin Məqsədi
Süni intellekt sistemlərinin (məsələn, RAG və ya LLM Agent-lərin) istehsalat mühitinə (production) buraxılmasından əvvəl onların dəqiqliyini və etibarlılığını ölçmək vacibdir. Bu freymvork aşağıdakıları təmin edir:

Standart və Kənar Halları (Edge Cases) əhatə edən test dəstinin formalaşdırılması.
LLM-as-a-Judge konseptindən istifadə edərək açıq-uclu cavabların insan müdaxiləsi olmadan qiymətləndirilməsi.
Sistem resurslarının (Latency, Token istifadəsi, Xərc) real vaxt rejimində izlənilməsi.

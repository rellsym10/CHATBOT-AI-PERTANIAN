"""
Evaluasi NLP Gemini menggunakan RAGAS — Rubrics Based Scoring
Metrik: Relevansi, Akurasi, Kejelasan (skala 1–5)
Jalankan: python ragas_eval_rubrics.py
"""

from ragas import evaluate
from ragas.metrics import RubricsScore
from ragas.dataset_schema import SingleTurnSample, EvaluationDataset
from langchain_openai import ChatOpenAI
from ragas.llms import LangchainLLMWrapper
import pandas as pd
import json

# ================================================================
# KONFIGURASI LLM (KoboiLLM / OpenAI-compatible)
# ================================================================
llm = ChatOpenAI(
    model="(SOLD OUT) anthropic/claude-sonnet-4-6",          # ganti model sesuai kebutuhan
    api_key="sk-aVP8hUiI8mnM5zz0PIC6mw",     # masukkan API Key KoboiLLM
    base_url="https://api.koboillm.com/v1",   # masukkan Base URL KoboiLLM
)
evaluator_llm = LangchainLLMWrapper(llm)


# ================================================================
# DEFINISI RUBRIK
# Skala 1–5 untuk setiap aspek, sesuai metodologi skripsi
# ================================================================

rubrik_relevansi = RubricsScore(
    name="relevansi",
    rubrics={
        "score1_description": (
            "Jawaban sama sekali tidak relevan dengan pertanyaan pertanian yang diajukan. "
            "Respons membahas topik yang tidak ada hubungannya dengan pertanyaan."
        ),
        "score2_description": (
            "Jawaban sedikit relevan tetapi sebagian besar menyimpang dari inti pertanyaan pertanian. "
            "Hanya menyentuh topik yang ditanyakan secara sepintas."
        ),
        "score3_description": (
            "Jawaban cukup relevan dengan pertanyaan pertanian, namun masih ada bagian yang "
            "tidak langsung menjawab inti pertanyaan atau terlalu umum."
        ),
        "score4_description": (
            "Jawaban relevan dan sebagian besar menjawab pertanyaan pertanian dengan baik. "
            "Hanya ada sedikit informasi tambahan yang kurang perlu."
        ),
        "score5_description": (
            "Jawaban sepenuhnya relevan, langsung menjawab inti pertanyaan pertanian, "
            "dan tidak mengandung informasi yang menyimpang dari topik yang ditanyakan."
        ),
    },
    llm=evaluator_llm,
)

rubrik_akurasi = RubricsScore(
    name="akurasi",
    rubrics={
        "score1_description": (
            "Informasi teknis pertanian dalam jawaban salah, menyesatkan, atau bertentangan "
            "dengan pengetahuan pertanian yang benar dan dapat merugikan petani."
        ),
        "score2_description": (
            "Sebagian besar informasi pertanian kurang tepat atau terdapat kesalahan teknis "
            "yang cukup signifikan dalam jawaban yang diberikan."
        ),
        "score3_description": (
            "Informasi umum pertanian benar, namun terdapat beberapa detail teknis yang "
            "kurang tepat, tidak lengkap, atau perlu diverifikasi lebih lanjut."
        ),
        "score4_description": (
            "Informasi pertanian sebagian besar akurat dan dapat dipertanggungjawabkan, "
            "dengan hanya sedikit ketidaktepatan minor yang tidak signifikan."
        ),
        "score5_description": (
            "Semua informasi teknis pertanian dalam jawaban akurat, sesuai dengan "
            "pengetahuan ilmiah/praktis pertanian, dan dapat dipertanggungjawabkan sepenuhnya."
        ),
    },
    llm=evaluator_llm,
)

rubrik_kejelasan = RubricsScore(
    name="kejelasan",
    rubrics={
        "score1_description": (
            "Jawaban sangat sulit dipahami, tidak terstruktur, menggunakan istilah teknis "
            "yang tidak dijelaskan, dan tidak cocok untuk petani awam."
        ),
        "score2_description": (
            "Jawaban agak sulit dipahami oleh petani awam. Struktur kurang jelas dan "
            "beberapa bagian membingungkan meskipun ada inti yang bisa ditangkap."
        ),
        "score3_description": (
            "Jawaban cukup jelas dan dapat dipahami, namun penyampaiannya kurang terstruktur "
            "atau beberapa bagian memerlukan penjelasan tambahan bagi petani awam."
        ),
        "score4_description": (
            "Jawaban jelas, cukup terstruktur, dan mudah dipahami oleh petani. "
            "Penggunaan bahasa sederhana dengan sedikit ruang untuk perbaikan."
        ),
        "score5_description": (
            "Jawaban sangat jelas, terstruktur dengan baik, menggunakan bahasa sederhana "
            "yang mudah dipahami petani awam, dan disajikan secara logis dan runtut."
        ),
    },
    llm=evaluator_llm,
)


# ================================================================
# DATA PENGUJIAN
# question  : pertanyaan dari pengguna chatbot
# response  : jawaban yang dihasilkan Gemini
# reference : jawaban referensi dari literatur/pakar pertanian
# ================================================================
data = [
    {
        "question": "Mengapa irigasi tetes lebih baik daripada irigasi banjir?",
        "response": (
            "Irigasi tetes lebih baik daripada irigasi banjir karena beberapa hal utama:\n\n💧 Hemat air: Air langsung diberikan ke akar tanaman, jadi tidak banyak yang terbuang karena menguap atau mengalir ke tempat lain. Irigasi banjir boros air.\n🌱 Nutrisi pas: Pupuk bisa dicampur dengan air irigasi tetes (fertigasi), jadi tanaman langsung dapat nutrisi yang dibutuhkan.\n🌿 Kurangi gulma: Hanya area sekitar tanaman yang basah, jadi gulma di antara barisan tanaman tidak tumbuh banyak.\n🦠 Kurangi penyakit: Daun tanaman tetap kering, sehingga mengurangi risiko penyakit jamur yang suka kondisi lembap.\n💪 Hasil lebih baik: Tanaman mendapatkan air dan nutrisi secara konsisten dan tepat, sehingga bisa tumbuh lebih sehat dan hasil panen lebih optimal."
        ),
        "reference": (
            "Irigasi tetes memiliki nilai efisiensi 80-95% dibandingkan dengan irigasi curah dan "
            "irigasi permukaan/banjir, karena air diberikan dalam volume kecil dan berkelanjutan "
            "langsung ke zona perakaran tanaman, sehingga terhindar dari kehilangan air akibat "
            "perkolasi dan limpasan permukaan. Sistem ini juga memungkinkan fertigasi (pemberian "
            "pupuk melalui air irigasi) dan mengurangi pertumbuhan gulma karena hanya area sekitar "
            "tanaman yang basah. "
            "Sumber: Kementerian PPN/Bappenas, kmc-pengairan.bappenas.go.id/knowledge-management/220"
        ),
    },
    {
        "question": "Apa peran penting plasma nutfah dalam pemuliaan tanaman?",
        "response": (
            "Plasma nutfah itu ibarat 'gudang' atau 'perpustakaan' semua jenis genetik tanaman yang ada, Pak/Bu. 📚 Isinya sifat-sifat baik dari berbagai tanaman.\n\nPeran pentingnya dalam pemuliaan tanaman adalah:\n1.  Sumber bahan baku: Petani atau peneliti bisa mencari sifat unggul dari situ, misalnya tanaman yang tahan penyakit, hasil panennya banyak, atau rasanya enak. 🌱\n2.  Menciptakan varietas baru: Dengan menggabungkan sifat-sifat ini, kita bisa membuat bibit tanaman baru yang lebih kuat, lebih produktif, dan lebih cocok untuk kondisi pertanian kita. 💪\n\nJadi, plasma nutfah ini sangat penting untuk menghasilkan tanaman yang lebih baik dan menguntungkan petani."
        ),
        "reference": (
            "Pemanfaatan plasma nutfah dalam program pemuliaan dilakukan melalui beberapa cara: "
            "pemanfaatan langsung aksesi plasma nutfah elit untuk dilepas sebagai varietas unggul, "
            "pemanfaatan aksesi sebagai donor gen untuk rekombinasi gen-gen unggul adaptif, serta "
            "sebagai bahan perluasan latar belakang genetik varietas melalui proses introgresi dan "
            "nobilisasi. Plasma nutfah merupakan sumber gen yang berguna bagi perbaikan tanaman, "
            "seperti gen untuk ketahanan terhadap hama, penyakit, dan kekeringan. "
            "Sumber: Sumarno, Buletin Plasma Nutfah, ejurnal.litbang.pertanian.go.id/index.php/bpn/article/view/5095"
        ),
    },
    {
        "question": "Tanaman tomat saya layu padahal sudah disiram, apa penyebabnya dan bagaimana solusinya?",
        "response": (
            "Halo Pak/Bu Tani, 🧑‍🌾\nTanaman tomat layu padahal sudah disiram bisa jadi karena beberapa hal.\n\n🌱 Penyakit / Masalah:\nLayu pada tanaman tomat meski sudah disiram.\n\n🔍 Penyebab:\n- Akar busuk: Terlalu banyak air atau tanah padat membuat akar tidak bisa bernapas dan menyerap air.\n- Penyakit layu bakteri atau layu fusarium: Penyakit ini menyumbat saluran air di dalam batang tanaman.\n- Hama nematoda: Cacing kecil di tanah yang merusak akar, sehingga akar tidak bisa menyerap air dengan baik.\n- Hama penggerek batang: Merusak batang sehingga aliran air dan nutrisi terhambat.\n\n🛠 Cara Penanganan:\n1.  Periksa akar dan batang. Coba gali sedikit tanah di sekitar pangkal batang, lihat apakah akarnya busuk atau ada benjolan (nematoda). Belah batang, lihat apakah ada bercak coklat atau hitam di dalamnya.\n2.  Pastikan tanah memiliki drainase yang baik. Jika tanah terlalu padat, gemburkan. Kurangi frekuensi penyiraman jika tanah masih basah.\n3.  Jika terbukti ada penyakit layu bakteri atau layu fusarium, segera cabut tanaman yang sakit dan buang jauh-jauh agar tidak menular ke tanaman lain.\n4.  Untuk hama nematoda, bisa gunakan mulsa plastik atau rotasi tanaman. Jika parah, bisa gunakan nematisida sesuai dosis.\n5.  Untuk hama penggerek batang, bersihkan gulma di sekitar tanaman dan bisa gunakan insektisida jika serangan parah."
        ),
        "reference": (
            "Penyakit layu fusarium disebabkan oleh cendawan patogen Fusarium oxysporum yang "
            "bersifat polifag dengan banyak tanaman inang, terutama sayuran seperti cabai, terong, "
            "dan tomat. Gejala awal berupa cabang bagian bawah tanaman terlihat layu dan daun tua "
            "menguning yang kemudian menjalar ke atas hingga tanaman mati. Selain itu, layu juga "
            "bisa disebabkan oleh layu bakteri (Ralstonia solanacearum) atau akar busuk akibat "
            "kelebihan air/drainase buruk. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/artikel/95068/"
            "pengendalian-penyakit-layu-fusarium---pada-tanaman-tomat-/"
        ),
    },
    {
        "question": "Bagaimana cara mengatasi hama ulat pada tanaman kubis secara alami?",
        "response": (
            "🌱 Hama Ulat Kubis:\nUlat ini suka makan daun kubis, bikin bolong-bolong dan bisa merusak tanaman sampai gagal panen. 🐛\n\n🔍 Penyebab:\n- Kupu-kupu atau ngengat meletakkan telurnya di daun kubis.\n- Lingkungan yang cocok untuk ulat berkembang biak.\n\n🛠 Cara Penanganan:\n1.  Ambil ulatnya langsung pakai tangan, lalu buang atau musnahkan. Lakukan rutin setiap pagi atau sore.\n2.  Semprot tanaman dengan larutan air sabun cuci piring (sedikit saja sabunnya) atau larutan bawang putih/cabai yang dihaluskan dan dicampur air.\n3.  Tanam tanaman pengusir hama di sekitar kubis, contohnya bunga marigold atau selasih.\n4.  Pastikan kebun bersih dari gulma yang bisa jadi tempat persembunyian ulat.\n5.  Gunakan bakteri Bacillus thuringiensis (Bt) yang aman untuk tanaman dan manusia. Ini bisa dibeli di toko pertanian dan disemprotkan ke daun."
        ),
        "reference": (
            "Pengendalian hama ulat daun kubis Plutella xylostella secara alami dapat dilakukan "
            "dengan insektisida bahan alami berupa ekstrak biji buah srikaya dan sirsak dengan "
            "konsentrasi 10%, serta ekstrak biji nimba dan tembakau. Selain itu, dapat memanfaatkan "
            "musuh alami seperti parasitoid Cotesia plutellae dan Diadegma semiclausum, serta "
            "insektisida biologi berbahan mikroba Bacillus thuringiensis (Bt) yang aman bagi "
            "lingkungan, manusia, dan hewan sekitar. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/artikel/97052/"
            "mengenal-hama-ulat-daun-kubis-plutella-xylostella-dan-teknik-pengendaliannya/"
        ),
    },
    {
        "question": "Pupuk apa yang cocok untuk mempercepat pertumbuhan jagung?",
        "response": (
            "Halo Pak/Bu Tani! 👋\n\nUntuk mempercepat pertumbuhan jagung, pupuk yang paling penting adalah yang kaya Nitrogen (N).\n\nBerikut pupuk yang cocok:\n\n1.  Urea:\n    *   Kaya Nitrogen, sangat bagus untuk daun dan batang biar cepat tinggi. 🌿\n\n2.  NPK (misal 16-16-16 atau yang lebih tinggi N):\n    *   Mengandung Nitrogen (N), Fosfor (P), dan Kalium (K) seimbang. N untuk daun, P untuk akar, K untuk kekuatan tanaman. 💪\n\n3.  ZA (Zwit Zuur Amonium):\n    *   Juga kaya Nitrogen, tapi ada sedikit belerang yang bagus untuk warna daun. 💚\n\nPenting: Berikan pupuk sesuai dosis dan waktu yang tepat ya, biasanya saat jagung masih kecil (umur 7-15 hari dan 25-35 hari setelah tanam)."
        ),
        "reference": (
            "Pemupukan berimbang pada tanaman jagung dilakukan dengan pemupukan susulan I pada "
            "umur tanaman sekitar 3 minggu menggunakan pupuk Majemuk NPK sebanyak 150-200 kg/ha, "
            "dan pemupukan susulan II pada umur sekitar 5 minggu (sekitar 36 HST) dengan pemberian "
            "pupuk Urea 100-150 kg/ha. Standar umum dosis pemupukan jagung adalah Urea 350 kg/ha, "
            "SP-36 200 kg/ha, dan KCl 100 kg/ha yang diberikan secara bertahap sebagai pupuk dasar "
            "dan dua kali pupuk susulan. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/mobile/artikel/76776/"
            "Pemupukan-Berimbang-Pada-Tanaman-Jagung-/"
        ),
    },
    {
        "question": "Cara budidaya tanaman cabai yang baik dan benar",
        "response": (
            "Halo Pak/Bu Tani! 👋\n\nIni cara budidaya cabai yang baik dan benar agar hasilnya melimpah:\n\n1.  Pemilihan Bibit 🌱\n    *   Pilih bibit dari varietas unggul yang tahan penyakit.\n    *   Pastikan bibit sehat, daun hijau segar, dan tidak ada tanda hama.\n    *   Bisa beli bibit siap tanam atau semai sendiri dari biji cabai yang bagus.\n\n2.  Persiapan Lahan 🚜\n    *   Bersihkan lahan dari rumput liar atau sisa tanaman sebelumnya.\n    *   Gemburkan tanah dengan dicangkul atau dibajak.\n    *   Buat bedengan (gundukan tanah) setinggi 30-40 cm dan lebar 1 meter. Jarak antar bedengan sekitar 50 cm.\n    *   Campurkan pupuk kandang atau kompos sekitar 2-3 kg per meter persegi ke bedengan, lalu diamkan 1-2 minggu.\n\n3.  Penanaman 🌶️\n    *   Buat lubang tanam di atas bedengan dengan jarak sekitar 60x70 cm.\n    *   Pindahkan bibit cabai dari polybag ke lubang tanam saat sore hari atau pagi hari.\n    *   Tanam bibit hati-hati agar akar tidak rusak, lalu timbun sedikit tanah dan padatkan perlahan.\n\n4.  Perawatan 💧\n    *   Penyiraman: Siram tanaman secara teratur, terutama saat musim kemarau. Jangan sampai tanah terlalu kering atau terlalu becek.\n    *   Pemupukan: Beri pupuk susulan sesuai dosis anjuran, biasanya pupuk NPK, setelah 2 minggu tanam dan diulang setiap 2-3 minggu sekali.\n    *   Penyiangan: Bersihkan rumput liar di sekitar tanaman agar tidak berebut nutrisi.\n    *   Pemasangan Ajir: Pasang tongkat penyangga (ajir) di dekat tanaman saat umur 2-3 minggu agar tanaman tidak roboh.\n    *   Pengendalian Hama dan Penyakit: Periksa tanaman secara rutin. Jika ada tanda hama atau penyakit, segera tangani sesuai jenisnya.\n\n5.  Panen 🧺\n    *   Cabai bisa mulai dipanen setelah umur 75-90 hari setelah tanam, tergantung jenis cabainya.\n    *   Panen saat buah cabai sudah berwarna merah penuh atau sesuai keinginan pasar.\n    *   Petik buah cabai beserta tangkainya agar lebih awet.\n    *   Panen bisa dilakukan berkali-kali (2-3 hari sekali) selama tanaman masih produktif."
        ),
        "reference": (
            "Jarak tanam ideal cabai pada musim kemarau adalah 60x60 cm dan pada musim penghujan "
            "diperlebar menjadi 70x70 cm untuk menjaga kelembaban udara di sekitar pertanaman. "
            "Pemupukan susulan dilakukan secara bertahap mulai umur 15 HST dan 30 HST dengan dosis "
            "3 kg NPK 15-15-15 per 200 liter air untuk 1000 tanaman, meningkat menjadi 4-5 kg pada "
            "umur 45-105 HST. Persiapan lahan meliputi pembuatan bedengan, pemberian kapur pertanian "
            "jika pH rendah, dan pemasangan mulsa plastik untuk menekan gulma. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/artikel/85527/budidaya-cabai/"
        ),
    },
    {
        "question": "Daun padi saya menguning dan ada bercak coklat, itu penyakit apa dan bagaimana mengatasinya?",
        "response": (
            "🌱 Penyakit / Masalah: Bercak Cokelat (Brown Spot)\nDaun padi menguning dan muncul bercak-bercak bulat atau oval berwarna cokelat gelap. Bercak ini bisa membesar dan menyebabkan daun kering.\n\n🔍 Penyebab:\n- Jamur Bipolaris oryzae.\n- Kekurangan unsur hara, terutama Kalium (K) atau Silika (Si).\n- Tanah kurang subur atau drainase buruk.\n\n🛠 Cara Penanganan:\n1.  Pilih varietas padi yang tahan penyakit.\n2.  Berikan pupuk berimbang sesuai kebutuhan tanah, terutama pupuk Kalium dan Silika.\n3.  Perbaiki pengairan dan drainase sawah.\n4.  Bersihkan sisa-sisa tanaman terinfeksi setelah panen.\n5.  Jika serangan parah, semprotkan fungisida yang dianjurkan untuk bercak cokelat."
        ),
        "reference": (
            "Penyakit bercak daun coklat (brown leaf spot) pada padi disebabkan oleh cendawan "
            "Helminthosporium oryzae/Bipolaris oryzae, ditandai bercak bulat kecil berwarna coklat "
            "gelap yang membesar dengan pusat berwarna kelabu. Fungisida Rabcide 50 WP dianjurkan "
            "untuk pengendalian, didukung pemupukan berimbang 250 kg urea, 100 kg SP-36, dan 100 kg "
            "KCl per ha, jarak tanam tidak terlalu rapat, serta penanaman varietas tahan seperti "
            "Ciherang. Gejala serupa juga bisa disebabkan penyakit Blast (Pyricularia oryzae) atau "
            "defisiensi nitrogen, sehingga diagnosis tepat memerlukan pengamatan lebih lanjut. "
            "Sumber: Cyber Extension Kementan (berdasarkan riset Pusat Penelitian Tanaman Pangan & "
            "BB Penelitian Tanaman Padi), cybex.pertanian.go.id/mobile/artikel/90421/"
            "Penyakit-Bercak-Daun-Pada-Tanaman-Padi/"
        ),
    },
    {
        "question": "Kapan waktu yang tepat untuk menanan padi",
        "response": (
            "Waktu terbaik menanam padi biasanya saat awal musim hujan. 🌧️ Ini karena padi butuh banyak air untuk tumbuh.\n\nDi daerah dengan irigasi yang baik, bisa juga tanam di musim kemarau asalkan pasokan airnya terjamin. 💧\n\nKuncinya adalah memastikan ketersediaan air yang cukup selama masa tanam."
        ),
        "reference": (
            "Waktu tanam padi ditentukan melalui Kalender Tanam Terpadu (KATAM) yang dikembangkan "
            "Badan Litbang Pertanian Kementan, yang dapat menentukan waktu tanam setiap musim "
            "(Musim Hujan/MH, MK-1, dan MK-2), pola tanam, rotasi tanam, dan rekomendasi teknologi "
            "pada skala kecamatan. KATAM juga memberikan informasi wilayah rawan kekeringan/banjir "
            "serta potensi serangan OPT, dan dapat diakses melalui katam.litbang.pertanian.go.id. "
            "Sumber: Cyber Extension Kementan, cybex.id/mobile/artikel/89739/"
            "KALENDER-TANAM-TERPADU-KATAM-TERPADU/"
        ),
    },
    {
        "question": "Apa fungsi pupuk NPK pada tanaman",
        "response": (
            "Halo Pak/Bu Tani! 👋\n\nPupuk NPK itu penting sekali untuk tanaman kita. NPK itu singkatan dari Nitrogen (N), Fosfor (P), dan Kalium (K). Ketiganya adalah nutrisi utama yang paling dibutuhkan tanaman supaya tumbuh subur dan hasil panennya bagus.\n\nIni fungsi masing-masingnya:\n\n🌱 Nitrogen (N):\n- Untuk pertumbuhan daun dan batang.\n- Membuat tanaman hijau royo-royo.\n- Penting di awal pertumbuhan.\n\n🌸 Fosfor (P):\n- Untuk pertumbuhan akar yang kuat.\n- Membantu pembentukan bunga dan buah.\n- Membuat tanaman lebih tahan penyakit.\n\n🥔 Kalium (K):\n- Untuk kualitas buah dan biji.\n- Membuat tanaman lebih kuat dari kekeringan atau penyakit.\n- Membantu proses fotosintesis.\n\nJadi, pupuk NPK itu seperti makanan lengkap supaya tanaman kita sehat, berdaun lebat, berakar kuat, berbunga banyak, dan berbuah lebat. 🍎🌿"
        ),
        "reference": (
            "Pupuk NPK merupakan pupuk majemuk yang mengandung tiga unsur hara makro: Nitrogen "
            "yang penting untuk klorofil sehingga membuat tanaman lebih hijau dan mendorong "
            "fotosintesis serta meningkatkan produksi daun; Fosfor yang merangsang pembentukan "
            "akar baru, memperkuat batang, serta merangsang pembentukan bunga dan buah; dan "
            "Kalium yang berfungsi sebagai aktivator enzim dalam proses metabolisme tanaman. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/mobile/artikel/81063/"
            "Manfaat-Pupuk-NPK-bagi-Tanaman/"
        ),
    },
    {
        "question": "Bagaimana cara mengatasi tanaman terong saya yg terkena jamur?",
        "response": (
            "🌱 Penyakit / Masalah: Jamur pada Terong\nDaun atau batang terong terlihat bercak, menguning, atau layu karena serangan jamur.\n\n🔍 Penyebab:\n- Kelembaban tinggi\n- Sirkulasi udara buruk\n- Tanaman terlalu rapat\n- Bibit atau tanah sudah terinfeksi\n- Nutrisi tanaman kurang seimbang\n\n🛠 Cara Penanganan:\n1. Buang bagian tanaman yang sakit dan bakar atau kubur jauh dari kebun.\n2. Semprot fungisida. Bisa pakai yang nabati (misal: ekstrak bawang putih) atau kimia sesuai dosis.\n3. Atur jarak tanam agar tidak terlalu rapat, supaya sirkulasi udara bagus.\n4. Kurangi kelembaban di sekitar tanaman, jangan terlalu sering menyiram atau menyiram di pagi hari.\n5. Beri pupuk yang seimbang agar tanaman kuat melawan penyakit."
        ),
        "reference": (
            "Penyakit jamur pada terong meliputi busuk buah yang disebabkan jamur Phytophthora "
            "sp., Phomopsis vexans, dan Phytium sp. dengan gejala bercak coklat kebasahan pada "
            "buah sehingga buah busuk (dikendalikan dengan fungisida), serta bercak daun yang "
            "disebabkan jamur Cercospora sp., Alternaria solani, dan Botrytis cinerea dengan "
            "gejala bercak kelabu-kecoklatan atau hitam pada daun. Pengendalian umum meliputi "
            "rotasi tanaman, sanitasi lahan, dan pengaturan jarak tanam serta drainase. "
            "Sumber: Cyber Extension Kementan, cybex.pertanian.go.id/artikel/97001/"
            "hama-dan-penyakit-pada-tanaman-terong/"
        ),
    },
]


# ================================================================
# BUAT DATASET RAGAS
# SingleTurnSample: user_input, response, reference
# ================================================================
def buat_dataset(data):
    samples = []
    for item in data:
        sample = SingleTurnSample(
            user_input=item["question"],
            response=item["response"],
            reference=item["reference"],
        )
        samples.append(sample)
    return EvaluationDataset(samples=samples)


# ================================================================
# JALANKAN EVALUASI UNTUK SATU METRIK
# ================================================================
def evaluasi_per_metrik(dataset, metrik):
    result = evaluate(
        dataset=dataset,
        metrics=[metrik],
    )
    return result.to_pandas()


# ================================================================
# TAMPILKAN HASIL GABUNGAN
# ================================================================
def tampilkan_dan_simpan_hasil(df_rel, df_aku, df_jelas):
    print("=" * 80)
    print("HASIL EVALUASI RAGAS — RUBRICS BASED SCORING")
    print("Chatbot NLP Gemini 2.5 Flash | Metode: LLM as a Judge")
    print("=" * 80)

    # Gabungkan kolom skor dari masing-masing DataFrame
    df_hasil = pd.DataFrame({
        "No": range(1, len(df_rel) + 1),
        "Pertanyaan": df_rel["user_input"],
        "Relevansi": df_rel["relevansi"].round(2),
        "Akurasi": df_aku["akurasi"].round(2),
        "Kejelasan": df_jelas["kejelasan"].round(2),
    })

    df_hasil["Rata-rata"] = df_hasil[["Relevansi", "Akurasi", "Kejelasan"]].mean(axis=1).round(2)

    # Cetak tabel
    header = f"{'No':<4}{'Pertanyaan':<48}{'Rel':<6}{'Aku':<6}{'Jls':<6}{'Avg'}"
    print(f"\n{header}")
    print("-" * 80)
    for _, row in df_hasil.iterrows():
        pertanyaan = str(row["Pertanyaan"])[:46]
        print(
            f"{int(row['No']):<4}"
            f"{pertanyaan:<48}"
            f"{row['Relevansi']:<6}"
            f"{row['Akurasi']:<6}"
            f"{row['Kejelasan']:<6}"
            f"{row['Rata-rata']}"
        )

    # Baris rata-rata keseluruhan
    print("-" * 80)
    avg_rel = df_hasil["Relevansi"].mean()
    avg_aku = df_hasil["Akurasi"].mean()
    avg_jls = df_hasil["Kejelasan"].mean()
    avg_all = df_hasil["Rata-rata"].mean()
    print(f"{'':4}{'Rata-rata Keseluruhan':<48}{avg_rel:<6.2f}{avg_aku:<6.2f}{avg_jls:<6.2f}{avg_all:.2f}")
    print("=" * 80)

    # Simpan ke file
    df_hasil.to_excel("hasil_ragas_rubrics.xlsx", index=False)
    df_hasil.to_json(
        "hasil_ragas_rubrics.json",
        orient="records",
        indent=2,
        force_ascii=False,
    )
    print("\n✅ Hasil disimpan ke: hasil_ragas_rubrics.xlsx dan hasil_ragas_rubrics.json")

    return df_hasil


# ================================================================
# MAIN
# ================================================================
if __name__ == "__main__":
    print("🌿 Membangun dataset evaluasi...")
    dataset = buat_dataset(data)
    print(f"✅ {len(dataset.samples)} sampel siap dievaluasi.\n")

    print("📊 Mengevaluasi RELEVANSI...")
    df_relevansi = evaluasi_per_metrik(dataset, rubrik_relevansi)

    print("📊 Mengevaluasi AKURASI...")
    df_akurasi = evaluasi_per_metrik(dataset, rubrik_akurasi)

    print("📊 Mengevaluasi KEJELASAN...")
    df_kejelasan = evaluasi_per_metrik(dataset, rubrik_kejelasan)

    df_final = tampilkan_dan_simpan_hasil(df_relevansi, df_akurasi, df_kejelasan)

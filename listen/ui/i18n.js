// Interface translations. English is the source; {0}, {1} are filled in by t().
// First versions by WildWard's AI assistant: native speakers, please send corrections to wildward.org@gmail.com.
const LANGS = { en: "English", id: "Bahasa Indonesia", ms: "Bahasa Melayu", vi: "Tiếng Việt", th: "ไทย", fil: "Filipino" };

const I18N = {
  "passes": { id: "rekaman lintasan", ms: "laluan", vi: "lượt bay", th: "ครั้งที่บินผ่าน", fil: "pagdaan" },
  "reviewed": { id: "diperiksa", ms: "disemak", vi: "đã xem xét", th: "ตรวจแล้ว", fil: "nasuri" },
  "Reference library": { id: "Pustaka referensi", ms: "Pustaka rujukan", vi: "Thư viện tham chiếu", th: "คลังเสียงอ้างอิง", fil: "Aklatan ng sanggunian" },
  "Open another survey": { id: "Buka survei lain", ms: "Buka tinjauan lain", vi: "Mở khảo sát khác", th: "เปิดการสำรวจอื่น", fil: "Magbukas ng ibang survey" },
  "Export": { id: "Ekspor", ms: "Eksport", vi: "Xuất", th: "ส่งออก", fil: "I-export" },
  "Share of passes reviewed": { id: "Bagian yang sudah diperiksa", ms: "Bahagian yang telah disemak", vi: "Tỷ lệ đã xem xét", th: "สัดส่วนที่ตรวจแล้ว", fil: "Bahaging nasuri na" },
  "Translations are a first draft. Corrections welcome: wildward.org@gmail.com": {
    id: "Terjemahan ini masih draf. Koreksi sangat kami harapkan: wildward.org@gmail.com",
    ms: "Terjemahan ini masih draf. Pembetulan dialu-alukan: wildward.org@gmail.com",
    vi: "Bản dịch này là bản nháp. Rất mong được góp ý: wildward.org@gmail.com",
    th: "คำแปลนี้เป็นฉบับร่าง ยินดีรับคำแก้ไข: wildward.org@gmail.com",
    fil: "Unang bersyon pa lang ang salin. Malugod naming tatanggapin ang mga pagtatama: wildward.org@gmail.com" },

  "Open a survey": { id: "Buka survei", ms: "Buka tinjauan", vi: "Mở khảo sát", th: "เปิดการสำรวจ", fil: "Magbukas ng survey" },
  "Point WildWard Listen at a folder of bat-detector recordings (WAV). It finds every bat pass, groups similar calls and measures them, all on this computer. Results are saved inside the folder, so you can close the app any time.": {
    id: "Pilih folder berisi rekaman detektor kelelawar (WAV). WildWard Listen menemukan setiap lintasan kelelawar, mengelompokkan suara yang mirip dan mengukurnya, semuanya di komputer ini. Hasil disimpan di dalam folder, jadi aplikasi bisa ditutup kapan saja.",
    ms: "Pilih folder rakaman pengesan kelawar (WAV). WildWard Listen mencari setiap laluan kelawar, mengumpulkan bunyi yang serupa dan mengukurnya, semuanya di komputer ini. Hasil disimpan di dalam folder, jadi aplikasi boleh ditutup bila-bila masa.",
    vi: "Chọn thư mục chứa bản ghi từ máy dò dơi (WAV). WildWard Listen tìm mọi lượt dơi bay qua, nhóm các tiếng kêu giống nhau và đo chúng, tất cả ngay trên máy tính này. Kết quả được lưu trong thư mục, nên bạn có thể đóng ứng dụng bất cứ lúc nào.",
    th: "เลือกโฟลเดอร์ไฟล์บันทึกเสียงจากเครื่องตรวจจับค้างคาว (WAV) WildWard Listen จะหาทุกครั้งที่ค้างคาวบินผ่าน จัดกลุ่มเสียงที่คล้ายกันและวัดค่า ทั้งหมดทำบนคอมพิวเตอร์เครื่องนี้ ผลลัพธ์บันทึกไว้ในโฟลเดอร์ จึงปิดโปรแกรมได้ทุกเมื่อ",
    fil: "Piliin ang folder ng mga recording mula sa bat detector (WAV). Hahanapin ng WildWard Listen ang bawat pagdaan ng paniki, pagsasamahin ang magkakatulad na tunog at susukatin ang mga ito, lahat sa computer na ito. Naka-save ang resulta sa loob ng folder, kaya puwede mong isara ang app anumang oras." },
  "Folder with recordings": { id: "Folder rekaman", ms: "Folder rakaman", vi: "Thư mục bản ghi", th: "โฟลเดอร์ไฟล์เสียง", fil: "Folder ng mga recording" },
  "How were the files recorded?": { id: "Bagaimana file direkam?", ms: "Bagaimana fail dirakam?", vi: "Tệp được ghi như thế nào?", th: "ไฟล์บันทึกด้วยวิธีใด", fil: "Paano ni-record ang mga file?" },
  "Real time (full-spectrum, 192 kHz or higher)": { id: "Waktu nyata (spektrum penuh, 192 kHz atau lebih)", ms: "Masa nyata (spektrum penuh, 192 kHz atau lebih)", vi: "Thời gian thực (toàn phổ, 192 kHz trở lên)", th: "เวลาจริง (เต็มสเปกตรัม 192 kHz ขึ้นไป)", fil: "Real time (full-spectrum, 192 kHz pataas)" },
  "Real time (192 kHz or higher)": { id: "Waktu nyata (192 kHz atau lebih)", ms: "Masa nyata (192 kHz atau lebih)", vi: "Thời gian thực (192 kHz trở lên)", th: "เวลาจริง (192 kHz ขึ้นไป)", fil: "Real time (192 kHz pataas)" },
  "Time-expanded 10x": { id: "Diperlambat 10x", ms: "Diperlahankan 10x", vi: "Giãn thời gian 10x", th: "ยืดเวลา 10 เท่า", fil: "Pinabagal nang 10x" },
  "Time-expanded 16x": { id: "Diperlambat 16x", ms: "Diperlahankan 16x", vi: "Giãn thời gian 16x", th: "ยืดเวลา 16 เท่า", fil: "Pinabagal nang 16x" },
  "Scan again even if results already exist": { id: "Pindai ulang meskipun hasil sudah ada", ms: "Imbas semula walaupun hasil sudah ada", vi: "Quét lại dù đã có kết quả", th: "สแกนใหม่แม้มีผลลัพธ์แล้ว", fil: "I-scan ulit kahit may resulta na" },
  "Scan recordings": { id: "Pindai rekaman", ms: "Imbas rakaman", vi: "Quét bản ghi", th: "สแกนไฟล์เสียง", fil: "I-scan ang mga recording" },

  "Teach WildWard Listen the species you already know. Pick a folder with one sub-folder per species, named exactly as it should appear, for example {0}. WildWard learns them before you review anything, then suggests species for this survey with a confidence score. Your own labels from this survey always count more than the library.": {
    id: "Ajari WildWard Listen spesies yang sudah Anda kenal. Pilih folder dengan satu subfolder per spesies, dinamai persis seperti yang ingin ditampilkan, misalnya {0}. WildWard mempelajarinya sebelum Anda memeriksa apa pun, lalu menyarankan spesies untuk survei ini beserta skor keyakinan. Label Anda sendiri dari survei ini selalu lebih berbobot daripada pustaka.",
    ms: "Ajar WildWard Listen spesies yang anda sudah kenal. Pilih folder dengan satu subfolder bagi setiap spesies, dinamakan tepat seperti yang patut dipaparkan, contohnya {0}. WildWard mempelajarinya sebelum anda menyemak apa-apa, kemudian mencadangkan spesies untuk tinjauan ini dengan skor keyakinan. Label anda sendiri daripada tinjauan ini sentiasa lebih diutamakan daripada pustaka.",
    vi: "Dạy WildWard Listen những loài bạn đã biết. Chọn thư mục có mỗi loài một thư mục con, đặt tên đúng như cần hiển thị, ví dụ {0}. WildWard học chúng trước khi bạn xem xét, rồi gợi ý loài cho khảo sát này kèm điểm tin cậy. Nhãn của bạn trong khảo sát này luôn được tính nặng hơn thư viện.",
    th: "สอน WildWard Listen ให้รู้จักชนิดที่คุณรู้จักอยู่แล้ว เลือกโฟลเดอร์ที่มีโฟลเดอร์ย่อยหนึ่งโฟลเดอร์ต่อหนึ่งชนิด ตั้งชื่อตามที่ต้องการให้แสดง เช่น {0} WildWard จะเรียนรู้ก่อนที่คุณจะตรวจ แล้วแนะนำชนิดสำหรับการสำรวจนี้พร้อมคะแนนความมั่นใจ ป้ายที่คุณติดเองในการสำรวจนี้มีน้ำหนักมากกว่าคลังเสียงเสมอ",
    fil: "Turuan ang WildWard Listen ng mga species na kilala mo na. Pumili ng folder na may isang sub-folder bawat species, na pinangalanan kung paano ito dapat lumabas, halimbawa {0}. Pag-aaralan ito ng WildWard bago ka magsuri, saka magmumungkahi ng species para sa survey na ito kasama ang confidence score. Laging mas mabigat ang sarili mong mga label sa survey na ito kaysa sa aklatan." },
  "Current library: {0}, {1} species, {2} reference passes.": { id: "Pustaka saat ini: {0}, {1} spesies, {2} lintasan referensi.", ms: "Pustaka semasa: {0}, {1} spesies, {2} laluan rujukan.", vi: "Thư viện hiện tại: {0}, {1} loài, {2} lượt tham chiếu.", th: "คลังปัจจุบัน: {0}, {1} ชนิด, {2} เสียงอ้างอิง", fil: "Kasalukuyang aklatan: {0}, {1} species, {2} sangguniang pagdaan." },
  "Reference folder": { id: "Folder referensi", ms: "Folder rujukan", vi: "Thư mục tham chiếu", th: "โฟลเดอร์อ้างอิง", fil: "Folder ng sanggunian" },
  "How were the reference files recorded?": { id: "Bagaimana file referensi direkam?", ms: "Bagaimana fail rujukan dirakam?", vi: "Tệp tham chiếu được ghi như thế nào?", th: "ไฟล์อ้างอิงบันทึกด้วยวิธีใด", fil: "Paano ni-record ang mga sangguniang file?" },
  "Mixed formats? Put a file named te.txt containing 10 or 16 inside any species folder that is time-expanded.": { id: "Format campuran? Taruh file bernama te.txt berisi 10 atau 16 di folder spesies yang diperlambat.", ms: "Format bercampur? Letakkan fail bernama te.txt yang mengandungi 10 atau 16 dalam folder spesies yang diperlahankan.", vi: "Định dạng lẫn lộn? Đặt tệp te.txt chứa 10 hoặc 16 vào thư mục loài nào được giãn thời gian.", th: "รูปแบบปนกัน? ใส่ไฟล์ชื่อ te.txt ที่มีเลข 10 หรือ 16 ในโฟลเดอร์ชนิดที่ยืดเวลา", fil: "Halo-halong format? Maglagay ng file na te.txt na may 10 o 16 sa loob ng bawat species folder na pinabagal." },
  "Learn species": { id: "Pelajari spesies", ms: "Pelajari spesies", vi: "Học loài", th: "เรียนรู้ชนิด", fil: "Pag-aralan ang species" },
  "Stop using this library": { id: "Berhenti memakai pustaka ini", ms: "Berhenti guna pustaka ini", vi: "Ngừng dùng thư viện này", th: "เลิกใช้คลังนี้", fil: "Itigil ang paggamit ng aklatang ito" },
  "Back to review": { id: "Kembali ke pemeriksaan", ms: "Kembali ke semakan", vi: "Quay lại xem xét", th: "กลับไปตรวจ", fil: "Bumalik sa pagsusuri" },
  "Type the reference folder first.": { id: "Ketik folder referensi dulu.", ms: "Taip folder rujukan dahulu.", vi: "Hãy nhập thư mục tham chiếu trước.", th: "พิมพ์โฟลเดอร์อ้างอิงก่อน", fil: "I-type muna ang folder ng sanggunian." },

  "Working…": { id: "Sedang bekerja…", ms: "Sedang berjalan…", vi: "Đang xử lý…", th: "กำลังทำงาน…", fil: "Ginagawa…" },
  "Finding bat calls, measuring them and comparing sounds. The first run on a big folder can take a while on a laptop. Results are cached, so next time is fast. You can leave this page open.": {
    id: "Mencari suara kelelawar, mengukurnya dan membandingkan suara. Pemindaian pertama folder besar bisa lama di laptop. Hasil disimpan, jadi berikutnya cepat. Biarkan halaman ini terbuka.",
    ms: "Mencari bunyi kelawar, mengukurnya dan membandingkan bunyi. Imbasan pertama folder besar mungkin mengambil masa di komputer riba. Hasil disimpan, jadi kali seterusnya lebih cepat. Biarkan halaman ini terbuka.",
    vi: "Đang tìm tiếng dơi, đo và so sánh âm thanh. Lần chạy đầu với thư mục lớn có thể mất một lúc trên laptop. Kết quả được lưu lại nên lần sau sẽ nhanh. Bạn có thể để trang này mở.",
    th: "กำลังหาเสียงค้างคาว วัดค่าและเปรียบเทียบเสียง ครั้งแรกกับโฟลเดอร์ใหญ่อาจใช้เวลาสักพักบนโน้ตบุ๊ก ผลลัพธ์ถูกเก็บไว้ ครั้งต่อไปจึงเร็ว เปิดหน้านี้ทิ้งไว้ได้",
    fil: "Hinahanap ang mga tunog ng paniki, sinusukat at pinaghahambing. Maaaring matagal ang unang takbo sa malaking folder sa laptop. Naka-save ang resulta kaya mabilis na sa susunod. Puwede mong iwanang bukas ang page na ito." },

  "To review": { id: "Perlu diperiksa", ms: "Perlu disemak", vi: "Cần xem xét", th: "รอตรวจ", fil: "Susuriin" },
  "All groups": { id: "Semua kelompok", ms: "Semua kumpulan", vi: "Tất cả nhóm", th: "ทุกกลุ่ม", fil: "Lahat ng grupo" },
  "Reviewed": { id: "Sudah diperiksa", ms: "Sudah disemak", vi: "Đã xem xét", th: "ตรวจแล้ว", fil: "Nasuri na" },
  "Night activity": { id: "Aktivitas malam", ms: "Aktiviti malam", vi: "Hoạt động ban đêm", th: "กิจกรรมยามค่ำ", fil: "Aktibidad sa gabi" },
  "Sites & nights": { id: "Lokasi & malam", ms: "Lokasi & malam", vi: "Địa điểm & đêm", th: "จุดและคืน", fil: "Lugar at gabi" },

  "Passes that sound alike are grouped together. Listen to a few, untick any that don't belong, type the species and label the whole group at once.": {
    id: "Lintasan yang suaranya mirip dikelompokkan. Dengarkan beberapa, hapus centang yang tidak cocok, ketik spesiesnya dan beri label seluruh kelompok sekaligus.",
    ms: "Laluan yang bunyinya serupa dikumpulkan bersama. Dengar beberapa, nyahtanda yang tidak sesuai, taip spesies dan labelkan seluruh kumpulan sekali gus.",
    vi: "Các lượt có âm thanh giống nhau được nhóm lại. Nghe vài lượt, bỏ chọn lượt không thuộc nhóm, nhập tên loài và gán nhãn cho cả nhóm một lần.",
    th: "ครั้งที่เสียงคล้ายกันถูกจัดเป็นกลุ่ม ฟังสักสองสามเสียง เอาเครื่องหมายออกจากเสียงที่ไม่เข้าพวก พิมพ์ชื่อชนิด แล้วติดป้ายทั้งกลุ่มในครั้งเดียว",
    fil: "Pinagsasama ang mga pagdaang magkatunog. Pakinggan ang ilan, alisin ang tsek sa hindi kasama, i-type ang species at lagyan ng label ang buong grupo nang sabay." },
  "Groups are ordered so the ones that teach WildWard the most come first.": { id: "Kelompok diurutkan agar yang paling banyak mengajari WildWard muncul lebih dulu.", ms: "Kumpulan disusun supaya yang paling banyak mengajar WildWard muncul dahulu.", vi: "Các nhóm được sắp xếp để nhóm dạy WildWard nhiều nhất hiện trước.", th: "เรียงกลุ่มให้กลุ่มที่สอน WildWard ได้มากที่สุดขึ้นก่อน", fil: "Nakaayos ang mga grupo para mauna ang mga pinakamakapagtuturo sa WildWard." },
  "Species suggestions come from your reference library ({0} species) plus your labels.": { id: "Saran spesies berasal dari pustaka referensi Anda ({0} spesies) ditambah label Anda.", ms: "Cadangan spesies datang daripada pustaka rujukan anda ({0} spesies) serta label anda.", vi: "Gợi ý loài đến từ thư viện tham chiếu của bạn ({0} loài) cùng các nhãn của bạn.", th: "คำแนะนำชนิดมาจากคลังอ้างอิงของคุณ ({0} ชนิด) และป้ายที่คุณติด", fil: "Galing ang mga mungkahing species sa iyong aklatan ({0} species) at sa mga label mo." },
  "Add a reference library, or label two species, and WildWard starts suggesting species for the rest.": { id: "Tambahkan pustaka referensi, atau beri label dua spesies, maka WildWard mulai menyarankan spesies untuk sisanya.", ms: "Tambah pustaka rujukan, atau labelkan dua spesies, dan WildWard mula mencadangkan spesies untuk selebihnya.", vi: "Thêm thư viện tham chiếu, hoặc gán nhãn hai loài, và WildWard bắt đầu gợi ý loài cho phần còn lại.", th: "เพิ่มคลังอ้างอิง หรือติดป้ายสองชนิด แล้ว WildWard จะเริ่มแนะนำชนิดให้ที่เหลือ", fil: "Magdagdag ng aklatan, o maglagay ng label sa dalawang species, at magsisimulang magmungkahi ang WildWard para sa iba." },
  "It can only suggest species it knows, so a bat missing from your library will be given the closest known species: always listen before confirming, and use \"Not in my library\" for bats it doesn't know. It learns from that too. Confidence scores appear once it knows five species.": {
    id: "Ia hanya bisa menyarankan spesies yang dikenalnya, jadi kelelawar yang tidak ada di pustaka akan diberi spesies terdekat: selalu dengarkan sebelum mengonfirmasi, dan gunakan \"Tidak ada di pustaka\" untuk kelelawar yang tidak dikenalnya. Ia juga belajar dari itu. Skor keyakinan muncul setelah ia mengenal lima spesies.",
    ms: "Ia hanya boleh mencadangkan spesies yang dikenalinya, jadi kelawar yang tiada dalam pustaka akan diberi spesies terdekat: sentiasa dengar sebelum mengesahkan, dan guna \"Tiada dalam pustaka\" untuk kelawar yang tidak dikenali. Ia juga belajar daripada itu. Skor keyakinan muncul apabila ia mengenali lima spesies.",
    vi: "Nó chỉ gợi ý được những loài nó biết, nên dơi không có trong thư viện sẽ bị gán loài gần nhất: luôn nghe trước khi xác nhận, và dùng \"Không có trong thư viện\" cho dơi nó không biết. Nó cũng học từ đó. Điểm tin cậy xuất hiện khi nó biết năm loài.",
    th: "ระบบแนะนำได้เฉพาะชนิดที่รู้จัก ค้างคาวที่ไม่มีในคลังจะถูกจับคู่กับชนิดที่ใกล้ที่สุด จึงควรฟังก่อนยืนยันเสมอ และใช้ปุ่ม \"ไม่มีในคลัง\" สำหรับค้างคาวที่ระบบไม่รู้จัก ระบบเรียนรู้จากสิ่งนี้ด้วย คะแนนความมั่นใจจะแสดงเมื่อรู้จักห้าชนิดขึ้นไป",
    fil: "Species lang na kilala nito ang maimumungkahi nito, kaya ang paniking wala sa aklatan ay bibigyan ng pinakamalapit na kilalang species: laging makinig bago kumpirmahin, at gamitin ang \"Wala sa aklatan ko\" para sa paniking hindi nito kilala. Natututo rin ito mula roon. Lalabas ang confidence score kapag lima na ang kilala nitong species." },
  "Everything is reviewed. Export the results when you're ready.": { id: "Semua sudah diperiksa. Ekspor hasilnya kapan pun Anda siap.", ms: "Semua sudah disemak. Eksport hasil apabila anda bersedia.", vi: "Đã xem xét xong. Xuất kết quả khi bạn sẵn sàng.", th: "ตรวจครบแล้ว ส่งออกผลได้เมื่อพร้อม", fil: "Nasuri na lahat. I-export ang resulta kapag handa ka na." },
  "Nothing here yet.": { id: "Belum ada apa-apa.", ms: "Belum ada apa-apa.", vi: "Chưa có gì.", th: "ยังไม่มีข้อมูล", fil: "Wala pa rito." },

  "Group {0}": { id: "Kelompok {0}", ms: "Kumpulan {0}", vi: "Nhóm {0}", th: "กลุ่ม {0}", fil: "Grupo {0}" },
  "{0} passes": { id: "{0} lintasan", ms: "{0} laluan", vi: "{0} lượt", th: "{0} ครั้ง", fil: "{0} pagdaan" },
  "calls around {0} kHz, {1} ms": { id: "suara sekitar {0} kHz, {1} ms", ms: "bunyi sekitar {0} kHz, {1} ms", vi: "tiếng kêu khoảng {0} kHz, {1} ms", th: "เสียงประมาณ {0} kHz, {1} ms", fil: "tunog na mga {0} kHz, {1} ms" },
  "Sound type:": { id: "Jenis suara:", ms: "Jenis bunyi:", vi: "Kiểu âm thanh:", th: "ลักษณะเสียง:", fil: "Uri ng tunog:" },
  "Show fewer": { id: "Tampilkan lebih sedikit", ms: "Tunjuk lebih sedikit", vi: "Ẩn bớt", th: "แสดงน้อยลง", fil: "Ipakita nang mas kaunti" },
  "Show all {0} passes": { id: "Tampilkan semua {0} lintasan", ms: "Tunjuk semua {0} laluan", vi: "Hiện cả {0} lượt", th: "แสดงทั้งหมด {0} ครั้ง", fil: "Ipakita lahat ng {0} pagdaan" },
  "Species or genus, e.g. Hipposideros larvatus": { id: "Spesies atau genus, mis. Hipposideros larvatus", ms: "Spesies atau genus, cth. Hipposideros larvatus", vi: "Loài hoặc chi, ví dụ Hipposideros larvatus", th: "ชนิดหรือสกุล เช่น Hipposideros larvatus", fil: "Species o genus, hal. Hipposideros larvatus" },
  "Label ticked passes": { id: "Beri label yang dicentang", ms: "Labelkan yang ditanda", vi: "Gán nhãn các lượt đã chọn", th: "ติดป้ายที่เลือก", fil: "Lagyan ng label ang mga may tsek" },
  "Not in my library": { id: "Tidak ada di pustaka", ms: "Tiada dalam pustaka", vi: "Không có trong thư viện", th: "ไม่มีในคลัง", fil: "Wala sa aklatan ko" },
  "For bats that aren't in your library. WildWard learns to send similar passes here instead of guessing a wrong species.": { id: "Untuk kelelawar yang tidak ada di pustaka Anda. WildWard belajar mengarahkan lintasan serupa ke sini alih-alih menebak spesies yang salah.", ms: "Untuk kelawar yang tiada dalam pustaka anda. WildWard belajar menghantar laluan serupa ke sini dan bukannya meneka spesies yang salah.", vi: "Dành cho dơi không có trong thư viện. WildWard học cách đưa các lượt tương tự vào đây thay vì đoán sai loài.", th: "สำหรับค้างคาวที่ไม่มีในคลัง WildWard จะเรียนรู้ที่จะส่งเสียงที่คล้ายกันมาที่นี่แทนการเดาชนิดผิด", fil: "Para sa mga paniking wala sa aklatan mo. Matututo ang WildWard na ipunta rito ang magkakatulad sa halip na manghula ng maling species." },
  "Clear labels": { id: "Hapus label", ms: "Kosongkan label", vi: "Xóa nhãn", th: "ล้างป้าย", fil: "Burahin ang mga label" },
  "suggested: {0}": { id: "saran: {0}", ms: "cadangan: {0}", vi: "gợi ý: {0}", th: "แนะนำ: {0}", fil: "mungkahi: {0}" },
  "(unsure)": { id: "(kurang yakin)", ms: "(kurang pasti)", vi: "(chưa chắc)", th: "(ไม่แน่ใจ)", fil: "(hindi sigurado)" },
  "probably {0} (genus)": { id: "kemungkinan {0} (genus)", ms: "mungkin {0} (genus)", vi: "có lẽ {0} (chi)", th: "น่าจะเป็น {0} (สกุล)", fil: "malamang {0} (genus)" },
  "closest of the {0} species it knows: {1}": { id: "paling mirip dari {0} spesies yang dikenal: {1}", ms: "paling hampir daripada {0} spesies yang dikenali: {1}", vi: "gần nhất trong {0} loài nó biết: {1}", th: "ใกล้ที่สุดใน {0} ชนิดที่รู้จัก: {1}", fil: "pinakamalapit sa {0} species na kilala nito: {1}" },
  "unusual": { id: "tidak biasa", ms: "luar biasa", vi: "bất thường", th: "ผิดปกติ", fil: "kakaiba" },
  "Unusual frequency": { id: "Frekuensi tidak biasa", ms: "Frekuensi luar biasa", vi: "Tần số bất thường", th: "ความถี่ผิดปกติ", fil: "Kakaibang frequency" },
  "{0} of {1} passes call around {2} kHz, at least 5% from every constant-frequency species you know (closest: {3}, {4} kHz). It may be a species missing from your library, or one worth a closer look. Listen carefully and check before labelling.": {
    id: "{0} dari {1} lintasan bersuara sekitar {2} kHz, setidaknya 5% dari setiap spesies berfrekuensi konstan yang Anda kenal (terdekat: {3}, {4} kHz). Bisa jadi spesies yang belum ada di pustaka, atau yang layak diperiksa lebih teliti. Dengarkan baik-baik sebelum memberi label.",
    ms: "{0} daripada {1} laluan berbunyi sekitar {2} kHz, sekurang-kurangnya 5% daripada setiap spesies berfrekuensi malar yang anda kenali (terdekat: {3}, {4} kHz). Mungkin spesies yang tiada dalam pustaka, atau yang wajar diteliti. Dengar dengan teliti sebelum melabel.",
    vi: "{0} trên {1} lượt kêu khoảng {2} kHz, cách mọi loài tần số không đổi bạn biết ít nhất 5% (gần nhất: {3}, {4} kHz). Có thể là loài chưa có trong thư viện, hoặc đáng xem kỹ hơn. Hãy nghe kỹ trước khi gán nhãn.",
    th: "{0} จาก {1} ครั้ง ส่งเสียงประมาณ {2} kHz ห่างจากทุกชนิดความถี่คงที่ที่คุณรู้จักอย่างน้อย 5% (ใกล้ที่สุด: {3}, {4} kHz) อาจเป็นชนิดที่ไม่มีในคลัง หรือควรตรวจดูให้ละเอียด ฟังให้ดีก่อนติดป้าย",
    fil: "{0} sa {1} pagdaan ang tumutunog nang mga {2} kHz, hindi bababa sa 5% ang layo sa bawat constant-frequency species na kilala mo (pinakamalapit: {3}, {4} kHz). Maaaring species na wala sa aklatan mo, o dapat suriing mabuti. Makinig nang mabuti bago maglagay ng label." },

  "Bat activity through the night": { id: "Aktivitas kelelawar sepanjang malam", ms: "Aktiviti kelawar sepanjang malam", vi: "Hoạt động của dơi suốt đêm", th: "กิจกรรมค้างคาวตลอดคืน", fil: "Aktibidad ng paniki buong gabi" },
  "Passes per hour, coloured by your labels, or by sound type where nothing is labelled yet. Times from: {0}.": { id: "Lintasan per jam, diwarnai menurut label Anda, atau jenis suara jika belum berlabel. Waktu dari: {0}.", ms: "Laluan sejam, diwarnakan mengikut label anda, atau jenis bunyi jika belum dilabel. Masa daripada: {0}.", vi: "Số lượt mỗi giờ, tô màu theo nhãn của bạn, hoặc theo kiểu âm thanh nếu chưa gán nhãn. Thời gian lấy từ: {0}.", th: "จำนวนครั้งต่อชั่วโมง ระบายสีตามป้ายของคุณ หรือตามลักษณะเสียงถ้ายังไม่ติดป้าย เวลาจาก: {0}", fil: "Pagdaan bawat oras, kinulayan ayon sa mga label mo, o sa uri ng tunog kung wala pang label. Oras mula sa: {0}." },
  "Open-air foragers (wind-turbine risk)": { id: "Pemburu di udara terbuka (risiko turbin angin)", ms: "Pemburu udara terbuka (risiko turbin angin)", vi: "Dơi săn mồi nơi thoáng (rủi ro tua-bin gió)", th: "ค้างคาวหากินในที่โล่ง (ความเสี่ยงกังหันลม)", fil: "Mga nanghuhuli sa bukas na himpapawid (panganib sa wind turbine)" },
  "Bats that hunt in open air, the group found flying at turbine height in Southeast Asia: {0} passes ({1} labelled, {2} by call shape only). Ground-level detectors under-sample bats at rotor height, so treat this as a lower bound.": {
    id: "Kelelawar yang berburu di udara terbuka, kelompok yang ditemukan terbang setinggi turbin di Asia Tenggara: {0} lintasan ({1} berlabel, {2} hanya dari bentuk suara). Detektor di permukaan tanah kurang menangkap kelelawar setinggi baling-baling, jadi anggap ini batas bawah.",
    ms: "Kelawar yang memburu di udara terbuka, kumpulan yang didapati terbang setinggi turbin di Asia Tenggara: {0} laluan ({1} dilabel, {2} berdasarkan bentuk bunyi sahaja). Pengesan di aras tanah kurang merakam kelawar setinggi bilah, jadi anggap ini had bawah.",
    vi: "Dơi săn mồi nơi thoáng, nhóm được ghi nhận bay ở độ cao tua-bin tại Đông Nam Á: {0} lượt ({1} đã gán nhãn, {2} chỉ theo hình dạng tiếng kêu). Máy dò đặt sát mặt đất ghi thiếu dơi ở độ cao cánh quạt, nên hãy coi đây là mức tối thiểu.",
    th: "ค้างคาวที่หากินในที่โล่ง กลุ่มที่พบบินที่ระดับความสูงของกังหันในเอเชียตะวันออกเฉียงใต้: {0} ครั้ง (ติดป้าย {1}, จากรูปแบบเสียงอย่างเดียว {2}) เครื่องที่วางระดับพื้นดินจับค้างคาวที่ระดับใบพัดได้น้อยกว่าจริง ให้ถือเป็นค่าต่ำสุด",
    fil: "Mga paniking nanghuhuli sa bukas na himpapawid, ang grupong nakitang lumilipad sa taas ng turbine sa Timog-Silangang Asya: {0} pagdaan ({1} may label, {2} batay lang sa hugis ng tunog). Kulang ang nahuhuli ng mga detector sa lupa sa taas ng elisi, kaya ituring itong pinakamababang bilang." },
  "Busiest nights: {0}.": { id: "Malam tersibuk: {0}.", ms: "Malam paling sibuk: {0}.", vi: "Những đêm nhộn nhịp nhất: {0}.", th: "คืนที่พลุกพล่านที่สุด: {0}", fil: "Pinakaabalang gabi: {0}." },
  "Summary": { id: "Ringkasan", ms: "Ringkasan", vi: "Tóm tắt", th: "สรุป", fil: "Buod" },
  "Group": { id: "Kelompok", ms: "Kumpulan", vi: "Nhóm", th: "กลุ่ม", fil: "Grupo" },
  "Passes": { id: "Lintasan", ms: "Laluan", vi: "Lượt", th: "ครั้ง", fil: "Pagdaan" },
  "No recording times found. Times are read from file names like 20261024_213000.wav.": { id: "Waktu rekaman tidak ditemukan. Waktu dibaca dari metadata detektor atau nama file seperti 20261024_213000.wav.", ms: "Masa rakaman tidak dijumpai. Masa dibaca daripada metadata pengesan atau nama fail seperti 20261024_213000.wav.", vi: "Không tìm thấy thời gian ghi. Thời gian được đọc từ siêu dữ liệu máy dò hoặc tên tệp như 20261024_213000.wav.", th: "ไม่พบเวลาบันทึก ระบบอ่านเวลาจากข้อมูลของเครื่องหรือชื่อไฟล์ เช่น 20261024_213000.wav", fil: "Walang nakitang oras ng recording. Binabasa ang oras mula sa metadata ng detector o sa pangalan ng file gaya ng 20261024_213000.wav." },
  "Detector sites": { id: "Lokasi detektor", ms: "Lokasi pengesan", vi: "Vị trí máy dò", th: "จุดวางเครื่อง", fil: "Mga lugar ng detector" },
  "Sites": { id: "Lokasi", ms: "Lokasi", vi: "Địa điểm", th: "จุด", fil: "Mga lugar" },
  "Detector": { id: "Detektor", ms: "Pengesan", vi: "Máy dò", th: "เครื่อง", fil: "Detector" },
  "Position": { id: "Posisi", ms: "Kedudukan", vi: "Tọa độ", th: "พิกัด", fil: "Posisyon" },
  "Device": { id: "Perangkat", ms: "Peranti", vi: "Thiết bị", th: "อุปกรณ์", fil: "Device" },
  "Files": { id: "File", ms: "Fail", vi: "Tệp", th: "ไฟล์", fil: "File" },
  "Most common": { id: "Paling sering", ms: "Paling kerap", vi: "Phổ biến nhất", th: "พบบ่อยที่สุด", fil: "Pinakakaraniwan" },
  "Activity night by night": { id: "Aktivitas per malam", ms: "Aktiviti setiap malam", vi: "Hoạt động theo từng đêm", th: "กิจกรรมรายคืน", fil: "Aktibidad bawat gabi" },
  "Type a species or genus first.": { id: "Ketik spesies atau genus dulu.", ms: "Taip spesies atau genus dahulu.", vi: "Hãy nhập loài hoặc chi trước.", th: "พิมพ์ชื่อชนิดหรือสกุลก่อน", fil: "I-type muna ang species o genus." },
  "Tick at least one pass.": { id: "Centang setidaknya satu lintasan.", ms: "Tanda sekurang-kurangnya satu laluan.", vi: "Hãy chọn ít nhất một lượt.", th: "เลือกอย่างน้อยหนึ่งครั้ง", fil: "Lagyan ng tsek ang kahit isang pagdaan." },
  "Labelled {0} passes as {1}.": { id: "{0} lintasan diberi label {1}.", ms: "{0} laluan dilabel sebagai {1}.", vi: "Đã gán nhãn {0} lượt là {1}.", th: "ติดป้าย {0} ครั้ง เป็น {1}", fil: "Nilagyan ng label na {1} ang {0} pagdaan." },
  "Cleared {0} labels.": { id: "{0} label dihapus.", ms: "{0} label dikosongkan.", vi: "Đã xóa {0} nhãn.", th: "ล้างป้าย {0} รายการ", fil: "Nabura ang {0} label." },
  "Saved in the survey folder (.wildward): passes.csv, calls.csv, report.html and occurrences.csv ({0} reviewed records in Darwin Core, ready for GBIF)": {
    id: "Disimpan di folder survei (.wildward): passes.csv, calls.csv, report.html dan occurrences.csv ({0} catatan terperiksa dalam format Darwin Core, siap untuk GBIF)",
    ms: "Disimpan dalam folder tinjauan (.wildward): passes.csv, calls.csv, report.html dan occurrences.csv ({0} rekod disemak dalam format Darwin Core, sedia untuk GBIF)",
    vi: "Đã lưu trong thư mục khảo sát (.wildward): passes.csv, calls.csv, report.html và occurrences.csv ({0} bản ghi đã xem xét theo chuẩn Darwin Core, sẵn sàng cho GBIF)",
    th: "บันทึกในโฟลเดอร์การสำรวจ (.wildward): passes.csv, calls.csv, report.html และ occurrences.csv ({0} บันทึกที่ตรวจแล้วในรูปแบบ Darwin Core พร้อมส่ง GBIF)",
    fil: "Naka-save sa folder ng survey (.wildward): passes.csv, calls.csv, report.html at occurrences.csv ({0} nasuring tala sa Darwin Core, handa para sa GBIF)" },
};

let LANG = "en";
try { LANG = localStorage.getItem("wildward-lang") || (navigator.language || "en").slice(0, 2); } catch (e) { /* storage blocked: default language */ }
if (LANG === "tl") LANG = "fil";
if (!LANGS[LANG]) LANG = "en";

function t(key, ...args) {
  const s = (LANG !== "en" && I18N[key] && I18N[key][LANG]) || key;
  return s.replace(/\{(\d)\}/g, (_, i) => args[+i] ?? "");
}

function setLang(code) {
  LANG = LANGS[code] ? code : "en";
  try { localStorage.setItem("wildward-lang", LANG); } catch (e) { /* not saved, still switches for this visit */ }
}

const totalPages = 604;
let currentPage = 1;

const img = document.getElementById('moshafPage');
const pageNumber = document.getElementById('pageNumber');
const pageInput = document.getElementById('pageInput');
const audio = document.getElementById('audioPlayer');
const loadingState = document.getElementById('loadingState');
const errorState = document.getElementById('errorState');

const pageSources = [
  (page) => `https://raw.githubusercontent.com/quran/quran.com-images/master/Pages/page${page}.png`,
  (page) => `https://cdn.jsdelivr.net/gh/quran/quran.com-images@master/Pages/page${page}.png`,
  (page) => `https://static.qurancdn.com/images/pages/page${Number(page)}.png`,
];

function formatPage(page) {
  return String(page).padStart(3, '0');
}

function updatePageState() {
  pageNumber.textContent = currentPage;
  pageInput.value = currentPage;
  localStorage.setItem('lastPage', String(currentPage));
}

function preloadImage(url) {
  return new Promise((resolve, reject) => {
    const probe = new Image();
    probe.onload = () => resolve(url);
    probe.onerror = reject;
    probe.referrerPolicy = 'no-referrer';
    probe.src = url;
  });
}

async function loadPage() {
  const formatted = formatPage(currentPage);
  loadingState.hidden = false;
  errorState.hidden = true;

  for (const sourceBuilder of pageSources) {
    const source = sourceBuilder(formatted);
    try {
      const resolved = await preloadImage(source);
      img.src = resolved;
      loadingState.hidden = true;
      updatePageState();
      return;
    } catch {
      // Try next provider.
    }
  }

  loadingState.hidden = true;
  errorState.hidden = false;
  img.removeAttribute('src');
  updatePageState();
}

function movePage(step) {
  const next = Math.min(totalPages, Math.max(1, currentPage + step));
  if (next !== currentPage) {
    currentPage = next;
    loadPage();
  }
}

function goToPage(page) {
  const parsed = Number(page);
  if (!Number.isInteger(parsed)) {
    return;
  }

  currentPage = Math.min(totalPages, Math.max(1, parsed));
  loadPage();
}

function playSurah() {
  const reciter = document.getElementById('reciter').value;
  let surah = Math.ceil(currentPage / 5);
  surah = Math.min(114, Math.max(1, surah));
  const surahCode = String(surah).padStart(3, '0');

  audio.src = `https://everyayah.com/data/${reciter}/${surahCode}001.mp3`;
  audio.play().catch(() => {
    // Browser may block autoplay without user interaction.
  });
}

function setupPrayerTimes() {
  const prayerTimes = document.getElementById('prayerTimes');
  if (!navigator.geolocation) {
    prayerTimes.textContent = 'الموقع غير مدعوم في هذا المتصفح.';
    return;
  }

  navigator.geolocation.getCurrentPosition(
    async (pos) => {
      try {
        const response = await fetch(
          `https://api.aladhan.com/v1/timings?latitude=${pos.coords.latitude}&longitude=${pos.coords.longitude}&method=5`,
        );
        const data = await response.json();
        const t = data.data.timings;
        prayerTimes.innerHTML = `
          الفجر: ${t.Fajr}<br>
          الظهر: ${t.Dhuhr}<br>
          العصر: ${t.Asr}<br>
          المغرب: ${t.Maghrib}<br>
          العشاء: ${t.Isha}
        `;
      } catch {
        prayerTimes.textContent = 'تعذر جلب المواقيت حالياً، حاول لاحقاً.';
      }
    },
    () => {
      prayerTimes.textContent = 'يرجى السماح بالموقع لعرض المواقيت بدقة.';
    },
    { timeout: 10000 },
  );
}

function setupTheme() {
  const themeBtn = document.getElementById('themeBtn');
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme === 'light') {
    document.body.classList.add('light');
  }

  themeBtn.addEventListener('click', () => {
    document.body.classList.toggle('light');
    localStorage.setItem('theme', document.body.classList.contains('light') ? 'light' : 'dark');
  });
}

function setupEvents() {
  document.getElementById('nextBtn').addEventListener('click', () => movePage(1));
  document.getElementById('prevBtn').addEventListener('click', () => movePage(-1));
  document.getElementById('playBtn').addEventListener('click', playSurah);

  pageInput.addEventListener('change', (event) => goToPage(event.target.value));

  document.addEventListener('keydown', (event) => {
    if (event.key === 'ArrowRight') {
      movePage(-1);
    }
    if (event.key === 'ArrowLeft') {
      movePage(1);
    }
  });
}

const savedPage = Number.parseInt(localStorage.getItem('lastPage') || '1', 10);
if (Number.isInteger(savedPage) && savedPage >= 1 && savedPage <= totalPages) {
  currentPage = savedPage;
}

setupEvents();
setupTheme();
setupPrayerTimes();
loadPage();

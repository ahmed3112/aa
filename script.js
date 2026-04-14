const STORAGE_KEY = 'fleetflow_bookings_v1';

const drivers = [
  { id: 'drv-101', name: 'Mohamed Hassan', phone: '+20 100 111 2233', vehicle: 'Toyota Hiace', plate: 'ف س ط 4381' },
  { id: 'drv-102', name: 'Youssef Adel', phone: '+20 101 225 9970', vehicle: 'Hyundai H1', plate: 'س ب ر 7214' },
  { id: 'drv-103', name: 'Ahmed Samir', phone: '+20 102 331 7449', vehicle: 'Mercedes Sprinter', plate: 'ر م ن 1159' },
  { id: 'drv-104', name: 'Karim Nabil', phone: '+20 109 441 5080', vehicle: 'Kia Carnival', plate: 'ع ل ج 9024' },
];

const bookingForm = document.getElementById('bookingForm');
const bookingRows = document.getElementById('bookingRows');
const rowTemplate = document.getElementById('rowTemplate');
const formMessage = document.getElementById('formMessage');
const tripType = document.getElementById('tripType');
const returnGroup = document.getElementById('returnGroup');
const returnTime = document.getElementById('returnTime');
const clearBtn = document.getElementById('clearBtn');

let bookings = loadBookings();

function loadBookings() {
  const raw = localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch {
    return [];
  }
}

function persistBookings() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(bookings));
}

function setFormMessage(text, type) {
  formMessage.textContent = text;
  formMessage.className = 'status';
  if (type) formMessage.classList.add(type);
}

function makeBookingId() {
  const today = new Date();
  const yy = String(today.getFullYear()).slice(-2);
  const mm = String(today.getMonth() + 1).padStart(2, '0');
  const dd = String(today.getDate()).padStart(2, '0');
  const suffix = String(Math.floor(Math.random() * 900) + 100);
  return `FLT-${yy}${mm}${dd}-${suffix}`;
}

function getDriverById(driverId) {
  return drivers.find((driver) => driver.id === driverId) || drivers[0];
}

function driverOptions(selectedId) {
  return drivers
    .map((driver) => {
      const selected = driver.id === selectedId ? 'selected' : '';
      return `<option value="${driver.id}" ${selected}>${driver.name} — ${driver.vehicle}</option>`;
    })
    .join('');
}

function formatTripSchedule(booking) {
  const returnSegment = booking.tripType === 'round-trip' && booking.returnTime ? ` | عودة: ${booking.returnTime}` : '';
  return `${booking.tripDate} | انطلاق: ${booking.tripTime}${returnSegment}`;
}

function createEmailLink(booking, driver) {
  const subject = `FleetFlow Booking ${booking.id} | Driver Details`;
  const bodyLines = [
    `Dear ${booking.requesterName},`,
    '',
    'Your fleet booking is confirmed with the following details:',
    `Booking ID: ${booking.id}`,
    `Trip Type: ${booking.tripType === 'round-trip' ? 'Round Trip' : 'One Way'}`,
    `Route: ${booking.pickup} -> ${booking.dropoff}`,
    `Passengers: ${booking.passengers}`,
    `Schedule: ${formatTripSchedule(booking)}`,
    '',
    'Assigned Driver Information:',
    `Driver Name: ${driver.name}`,
    `Driver Phone: ${driver.phone}`,
    `Vehicle: ${driver.vehicle}`,
    `Plate Number: ${driver.plate}`,
    '',
    `Notes: ${booking.notes || 'N/A'}`,
    '',
    'Thanks,',
    'Fleet Operations Team',
  ];

  const encodedSubject = encodeURIComponent(subject);
  const encodedBody = encodeURIComponent(bodyLines.join('\n'));
  return `mailto:${booking.requesterEmail}?subject=${encodedSubject}&body=${encodedBody}`;
}

function renderBookings() {
  bookingRows.innerHTML = '';

  if (!bookings.length) {
    bookingRows.innerHTML = '<tr><td class="empty" colspan="6">لا توجد حجوزات حالياً. أضف أول طلب الآن.</td></tr>';
    return;
  }

  for (const booking of bookings) {
    const row = rowTemplate.content.firstElementChild.cloneNode(true);
    row.querySelector('.cell-id').textContent = booking.id;
    row.querySelector('.cell-requester').textContent = `${booking.requesterName} (${booking.requesterEmail})`;
    row.querySelector('.cell-route').textContent = `${booking.pickup} ← ${booking.dropoff}`;
    row.querySelector('.cell-schedule').textContent = formatTripSchedule(booking);

    const select = row.querySelector('.driver-select');
    select.innerHTML = driverOptions(booking.driverId);
    select.addEventListener('change', (event) => {
      booking.driverId = event.target.value;
      persistBookings();
      renderBookings();
    });

    const chosenDriver = getDriverById(booking.driverId);
    const actionContainer = row.querySelector('.cell-actions');
    const emailBtn = document.createElement('a');
    emailBtn.className = 'email-btn';
    emailBtn.href = createEmailLink(booking, chosenDriver);
    emailBtn.target = '_blank';
    emailBtn.rel = 'noreferrer';
    emailBtn.textContent = 'إرسال بريد';
    emailBtn.setAttribute('role', 'button');
    actionContainer.appendChild(emailBtn);

    bookingRows.appendChild(row);
  }
}

function getFormData() {
  return {
    requesterName: document.getElementById('requesterName').value.trim(),
    requesterEmail: document.getElementById('requesterEmail').value.trim(),
    tripType: document.getElementById('tripType').value,
    passengers: Number(document.getElementById('passengers').value),
    pickup: document.getElementById('pickup').value.trim(),
    dropoff: document.getElementById('dropoff').value.trim(),
    tripDate: document.getElementById('tripDate').value,
    tripTime: document.getElementById('tripTime').value,
    returnTime: returnTime.value,
    notes: document.getElementById('notes').value.trim(),
  };
}

function validateBooking(data) {
  if (!data.requesterName || !data.requesterEmail || !data.pickup || !data.dropoff || !data.tripDate || !data.tripTime) {
    return 'يرجى استكمال كل الحقول الأساسية.';
  }

  if (!data.requesterEmail.includes('@')) {
    return 'صيغة البريد الإلكتروني غير صحيحة.';
  }

  if (data.passengers < 1 || data.passengers > 20) {
    return 'عدد الركاب يجب أن يكون من 1 إلى 20.';
  }

  if (data.tripType === 'round-trip' && !data.returnTime) {
    return 'يرجى تحديد وقت العودة لرحلة الذهاب والعودة.';
  }

  return '';
}

tripType.addEventListener('change', () => {
  const isRoundTrip = tripType.value === 'round-trip';
  returnGroup.hidden = !isRoundTrip;
  returnTime.required = isRoundTrip;
  if (!isRoundTrip) returnTime.value = '';
});

bookingForm.addEventListener('submit', (event) => {
  event.preventDefault();
  const data = getFormData();
  const validationError = validateBooking(data);

  if (validationError) {
    setFormMessage(validationError, 'error');
    return;
  }

  bookings.unshift({
    ...data,
    id: makeBookingId(),
    driverId: drivers[0].id,
    createdAt: new Date().toISOString(),
  });

  persistBookings();
  renderBookings();
  bookingForm.reset();
  tripType.value = 'one-way';
  tripType.dispatchEvent(new Event('change'));
  setFormMessage('تم إضافة الطلب بنجاح وتعيين سائق افتراضي.', 'success');
});

clearBtn.addEventListener('click', () => {
  bookings = [];
  persistBookings();
  renderBookings();
  setFormMessage('تم مسح جميع الطلبات.', 'success');
});

tripType.dispatchEvent(new Event('change'));
renderBookings();

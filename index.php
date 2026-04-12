<?php
require __DIR__ . '/db.php';
require __DIR__ . '/helpers.php';

$config = require __DIR__ . '/config.php';

$doctors = $pdo->query('SELECT id, full_name, specialty FROM doctors WHERE is_active = 1 ORDER BY full_name')->fetchAll();
$services = $pdo->query('SELECT id, service_name, duration_minutes FROM services WHERE is_active = 1 ORDER BY service_name')->fetchAll();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $patientName = trim($_POST['patient_name'] ?? '');
    $phone = trim($_POST['phone'] ?? '');
    $doctorId = (int)($_POST['doctor_id'] ?? 0);
    $serviceId = (int)($_POST['service_id'] ?? 0);
    $appointmentDate = trim($_POST['appointment_date'] ?? '');
    $appointmentTime = trim($_POST['appointment_time'] ?? '');
    $notes = trim($_POST['notes'] ?? '');

    if ($patientName === '' || !valid_phone($phone) || !$doctorId || !$serviceId || $appointmentDate === '' || $appointmentTime === '') {
        flash('danger', 'من فضلك أدخل كل البيانات بشكل صحيح.');
        header('Location: /index.php');
        exit;
    }

    $appointmentAt = date('Y-m-d H:i:s', strtotime($appointmentDate . ' ' . $appointmentTime));
    if (!$appointmentAt || strtotime($appointmentAt) < time()) {
        flash('danger', 'ميعاد الحجز يجب أن يكون في المستقبل.');
        header('Location: /index.php');
        exit;
    }

    $check = $pdo->prepare('SELECT COUNT(*) FROM appointments WHERE doctor_id = ? AND appointment_at = ? AND status IN ("pending", "confirmed")');
    $check->execute([$doctorId, $appointmentAt]);
    if ((int)$check->fetchColumn() > 0) {
        flash('danger', 'هذا الموعد محجوز بالفعل، اختر وقت آخر.');
        header('Location: /index.php');
        exit;
    }

    $stmt = $pdo->prepare('INSERT INTO appointments (patient_name, phone, doctor_id, service_id, appointment_at, notes, status, created_at) VALUES (?, ?, ?, ?, ?, ?, "pending", NOW())');
    $stmt->execute([$patientName, $phone, $doctorId, $serviceId, $appointmentAt, $notes]);

    flash('success', 'تم تسجيل الحجز بنجاح. تابع الحجز من صفحة متابعة الحجوزات.');
    header('Location: /my_bookings.php?phone=' . urlencode($phone));
    exit;
}
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title><?= e($config['clinic_name']) ?> - حجز موعد</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0"><?= e($config['clinic_name']) ?> - حجز موعد</h1>
    <div>
      <a class="btn btn-outline-primary btn-sm" href="/my_bookings.php">متابعة حجوزاتي</a>
      <a class="btn btn-outline-dark btn-sm" href="/admin_login.php">لوحة الإدارة</a>
    </div>
  </div>

  <?php foreach (get_flashes() as $flash): ?>
    <div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
  <?php endforeach; ?>

  <div class="card shadow-sm">
    <div class="card-body">
      <form method="post" class="row g-3">
        <div class="col-md-6">
          <label class="form-label">اسم المريض</label>
          <input type="text" name="patient_name" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">رقم الهاتف</label>
          <input type="text" name="phone" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">الطبيب</label>
          <select name="doctor_id" class="form-select" required>
            <option value="">اختر الطبيب</option>
            <?php foreach ($doctors as $doctor): ?>
              <option value="<?= (int)$doctor['id'] ?>"><?= e($doctor['full_name']) ?> - <?= e($doctor['specialty']) ?></option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">الخدمة</label>
          <select name="service_id" class="form-select" required>
            <option value="">اختر الخدمة</option>
            <?php foreach ($services as $service): ?>
              <option value="<?= (int)$service['id'] ?>"><?= e($service['service_name']) ?> (<?= (int)$service['duration_minutes'] ?> دقيقة)</option>
            <?php endforeach; ?>
          </select>
        </div>
        <div class="col-md-6">
          <label class="form-label">تاريخ الموعد</label>
          <input type="date" name="appointment_date" class="form-control" required>
        </div>
        <div class="col-md-6">
          <label class="form-label">وقت الموعد</label>
          <input type="time" name="appointment_time" class="form-control" required>
        </div>
        <div class="col-12">
          <label class="form-label">ملاحظات إضافية</label>
          <textarea name="notes" class="form-control" rows="3"></textarea>
        </div>
        <div class="col-12">
          <button class="btn btn-primary">تأكيد الحجز</button>
        </div>
      </form>
    </div>
  </div>
</div>
</body>
</html>

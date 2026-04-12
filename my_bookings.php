<?php
require __DIR__ . '/db.php';
require __DIR__ . '/helpers.php';

$phone = trim($_GET['phone'] ?? $_POST['phone'] ?? '');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['cancel_id'])) {
    $cancelId = (int)$_POST['cancel_id'];
    $phoneInput = trim($_POST['phone'] ?? '');
    $stmt = $pdo->prepare('UPDATE appointments SET status = "cancelled" WHERE id = ? AND phone = ? AND status IN ("pending", "confirmed")');
    $stmt->execute([$cancelId, $phoneInput]);
    flash('success', 'تم إلغاء الحجز بنجاح.');
    header('Location: /my_bookings.php?phone=' . urlencode($phoneInput));
    exit;
}

$bookings = [];
if ($phone !== '' && valid_phone($phone)) {
    $stmt = $pdo->prepare('SELECT a.id, a.patient_name, a.phone, a.appointment_at, a.status, a.notes, d.full_name AS doctor_name, s.service_name
                           FROM appointments a
                           JOIN doctors d ON d.id = a.doctor_id
                           JOIN services s ON s.id = a.service_id
                           WHERE a.phone = ?
                           ORDER BY a.appointment_at DESC');
    $stmt->execute([$phone]);
    $bookings = $stmt->fetchAll();
}
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>متابعة حجوزاتي</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3">متابعة حجوزاتي</h1>
    <a href="/index.php" class="btn btn-outline-secondary btn-sm">عودة للحجز</a>
  </div>

  <?php foreach (get_flashes() as $flash): ?>
    <div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
  <?php endforeach; ?>

  <div class="card mb-3">
    <div class="card-body">
      <form method="get" class="row g-2">
        <div class="col-md-8">
          <input type="text" name="phone" class="form-control" placeholder="اكتب رقم الهاتف" value="<?= e($phone) ?>" required>
        </div>
        <div class="col-md-4">
          <button class="btn btn-primary w-100">عرض الحجوزات</button>
        </div>
      </form>
    </div>
  </div>

  <?php if ($phone !== '' && !valid_phone($phone)): ?>
    <div class="alert alert-danger">رقم الهاتف غير صحيح.</div>
  <?php endif; ?>

  <?php if ($bookings): ?>
    <div class="table-responsive bg-white shadow-sm rounded">
      <table class="table table-striped mb-0">
        <thead>
          <tr>
            <th>المريض</th>
            <th>الطبيب</th>
            <th>الخدمة</th>
            <th>الموعد</th>
            <th>الحالة</th>
            <th>إجراء</th>
          </tr>
        </thead>
        <tbody>
        <?php foreach ($bookings as $booking): ?>
          <tr>
            <td><?= e($booking['patient_name']) ?></td>
            <td><?= e($booking['doctor_name']) ?></td>
            <td><?= e($booking['service_name']) ?></td>
            <td><?= e(date('Y-m-d h:i A', strtotime($booking['appointment_at']))) ?></td>
            <td><?= e($booking['status']) ?></td>
            <td>
              <?php if (in_array($booking['status'], ['pending', 'confirmed'], true)): ?>
                <form method="post" onsubmit="return confirm('هل تريد إلغاء الحجز؟')">
                  <input type="hidden" name="phone" value="<?= e($phone) ?>">
                  <input type="hidden" name="cancel_id" value="<?= (int)$booking['id'] ?>">
                  <button class="btn btn-sm btn-danger">إلغاء</button>
                </form>
              <?php else: ?>
                -
              <?php endif; ?>
            </td>
          </tr>
        <?php endforeach; ?>
        </tbody>
      </table>
    </div>
  <?php elseif ($phone !== ''): ?>
    <div class="alert alert-warning">لا توجد حجوزات لهذا الرقم.</div>
  <?php endif; ?>
</div>
</body>
</html>

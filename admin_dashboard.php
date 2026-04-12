<?php
require __DIR__ . '/db.php';
require __DIR__ . '/helpers.php';
require_admin();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $action = $_POST['action'] ?? '';

    if ($action === 'add_doctor') {
        $name = trim($_POST['full_name'] ?? '');
        $specialty = trim($_POST['specialty'] ?? '');
        if ($name && $specialty) {
            $stmt = $pdo->prepare('INSERT INTO doctors (full_name, specialty, is_active) VALUES (?, ?, 1)');
            $stmt->execute([$name, $specialty]);
            flash('success', 'تمت إضافة الطبيب.');
        }
    }

    if ($action === 'toggle_doctor') {
        $id = (int)($_POST['id'] ?? 0);
        $stmt = $pdo->prepare('UPDATE doctors SET is_active = 1 - is_active WHERE id = ?');
        $stmt->execute([$id]);
        flash('success', 'تم تحديث حالة الطبيب.');
    }

    if ($action === 'add_service') {
        $serviceName = trim($_POST['service_name'] ?? '');
        $duration = (int)($_POST['duration_minutes'] ?? 0);
        if ($serviceName && $duration > 0) {
            $stmt = $pdo->prepare('INSERT INTO services (service_name, duration_minutes, is_active) VALUES (?, ?, 1)');
            $stmt->execute([$serviceName, $duration]);
            flash('success', 'تمت إضافة الخدمة.');
        }
    }

    if ($action === 'toggle_service') {
        $id = (int)($_POST['id'] ?? 0);
        $stmt = $pdo->prepare('UPDATE services SET is_active = 1 - is_active WHERE id = ?');
        $stmt->execute([$id]);
        flash('success', 'تم تحديث حالة الخدمة.');
    }

    if ($action === 'change_status') {
        $id = (int)($_POST['id'] ?? 0);
        $status = $_POST['status'] ?? 'pending';
        if (in_array($status, ['pending', 'confirmed', 'completed', 'cancelled'], true)) {
            $stmt = $pdo->prepare('UPDATE appointments SET status = ? WHERE id = ?');
            $stmt->execute([$status, $id]);
            flash('success', 'تم تحديث حالة الحجز.');
        }
    }

    header('Location: /admin_dashboard.php');
    exit;
}

$doctors = $pdo->query('SELECT * FROM doctors ORDER BY id DESC')->fetchAll();
$services = $pdo->query('SELECT * FROM services ORDER BY id DESC')->fetchAll();
$appointments = $pdo->query('SELECT a.*, d.full_name AS doctor_name, s.service_name FROM appointments a JOIN doctors d ON d.id = a.doctor_id JOIN services s ON s.id = a.service_id ORDER BY a.appointment_at DESC')->fetchAll();
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>لوحة الإدارة</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
</head>
<body class="bg-light">
<div class="container py-4">
  <div class="d-flex justify-content-between align-items-center mb-3">
    <h1 class="h3 mb-0">لوحة إدارة العيادة</h1>
    <div>
      <a class="btn btn-outline-secondary btn-sm" href="/index.php">واجهة الحجز</a>
      <a class="btn btn-dark btn-sm" href="/admin_logout.php">تسجيل خروج</a>
    </div>
  </div>

  <?php foreach (get_flashes() as $flash): ?>
    <div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
  <?php endforeach; ?>

  <div class="row g-3 mb-3">
    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h2 class="h5">إدارة الأطباء</h2>
          <form method="post" class="row g-2 mb-3">
            <input type="hidden" name="action" value="add_doctor">
            <div class="col-md-5"><input class="form-control" name="full_name" placeholder="اسم الطبيب" required></div>
            <div class="col-md-5"><input class="form-control" name="specialty" placeholder="التخصص" required></div>
            <div class="col-md-2"><button class="btn btn-primary w-100">إضافة</button></div>
          </form>
          <ul class="list-group">
            <?php foreach ($doctors as $doctor): ?>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                <span><?= e($doctor['full_name']) ?> - <?= e($doctor['specialty']) ?> (<?= $doctor['is_active'] ? 'مفعل' : 'مغلق' ?>)</span>
                <form method="post">
                  <input type="hidden" name="action" value="toggle_doctor">
                  <input type="hidden" name="id" value="<?= (int)$doctor['id'] ?>">
                  <button class="btn btn-sm btn-outline-dark">تغيير الحالة</button>
                </form>
              </li>
            <?php endforeach; ?>
          </ul>
        </div>
      </div>
    </div>

    <div class="col-md-6">
      <div class="card h-100">
        <div class="card-body">
          <h2 class="h5">إدارة الخدمات</h2>
          <form method="post" class="row g-2 mb-3">
            <input type="hidden" name="action" value="add_service">
            <div class="col-md-6"><input class="form-control" name="service_name" placeholder="اسم الخدمة" required></div>
            <div class="col-md-4"><input type="number" min="5" class="form-control" name="duration_minutes" placeholder="المدة" required></div>
            <div class="col-md-2"><button class="btn btn-primary w-100">إضافة</button></div>
          </form>
          <ul class="list-group">
            <?php foreach ($services as $service): ?>
              <li class="list-group-item d-flex justify-content-between align-items-center">
                <span><?= e($service['service_name']) ?> - <?= (int)$service['duration_minutes'] ?> دقيقة (<?= $service['is_active'] ? 'مفعلة' : 'مغلقة' ?>)</span>
                <form method="post">
                  <input type="hidden" name="action" value="toggle_service">
                  <input type="hidden" name="id" value="<?= (int)$service['id'] ?>">
                  <button class="btn btn-sm btn-outline-dark">تغيير الحالة</button>
                </form>
              </li>
            <?php endforeach; ?>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <div class="card">
    <div class="card-body">
      <h2 class="h5">كل الحجوزات</h2>
      <div class="table-responsive">
        <table class="table table-striped">
          <thead>
            <tr>
              <th>#</th><th>المريض</th><th>الهاتف</th><th>الطبيب</th><th>الخدمة</th><th>الموعد</th><th>الحالة</th><th>تحديث</th>
            </tr>
          </thead>
          <tbody>
            <?php foreach ($appointments as $appointment): ?>
              <tr>
                <td><?= (int)$appointment['id'] ?></td>
                <td><?= e($appointment['patient_name']) ?></td>
                <td><?= e($appointment['phone']) ?></td>
                <td><?= e($appointment['doctor_name']) ?></td>
                <td><?= e($appointment['service_name']) ?></td>
                <td><?= e(date('Y-m-d h:i A', strtotime($appointment['appointment_at']))) ?></td>
                <td><?= e($appointment['status']) ?></td>
                <td>
                  <form method="post" class="d-flex gap-2">
                    <input type="hidden" name="action" value="change_status">
                    <input type="hidden" name="id" value="<?= (int)$appointment['id'] ?>">
                    <select class="form-select form-select-sm" name="status">
                      <?php foreach (['pending', 'confirmed', 'completed', 'cancelled'] as $status): ?>
                        <option value="<?= $status ?>" <?= $appointment['status'] === $status ? 'selected' : '' ?>><?= $status ?></option>
                      <?php endforeach; ?>
                    </select>
                    <button class="btn btn-sm btn-success">حفظ</button>
                  </form>
                </td>
              </tr>
            <?php endforeach; ?>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</div>
</body>
</html>

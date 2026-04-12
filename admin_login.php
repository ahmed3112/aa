<?php
require __DIR__ . '/helpers.php';
$config = require __DIR__ . '/config.php';

if (is_admin()) {
    header('Location: /admin_dashboard.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $username = trim($_POST['username'] ?? '');
    $password = trim($_POST['password'] ?? '');

    if ($username === $config['admin_user'] && $password === $config['admin_pass']) {
        $_SESSION['admin_logged_in'] = true;
        flash('success', 'تم تسجيل الدخول بنجاح.');
        header('Location: /admin_dashboard.php');
        exit;
    }

    flash('danger', 'بيانات الدخول غير صحيحة.');
    header('Location: /admin_login.php');
    exit;
}
?>
<!doctype html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>دخول الإدارة</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.rtl.min.css" rel="stylesheet">
</head>
<body class="bg-light d-flex align-items-center" style="min-height:100vh">
<div class="container" style="max-width:420px;">
  <?php foreach (get_flashes() as $flash): ?>
    <div class="alert alert-<?= e($flash['type']) ?>"><?= e($flash['message']) ?></div>
  <?php endforeach; ?>
  <div class="card shadow-sm">
    <div class="card-body">
      <h1 class="h4 mb-3">تسجيل دخول الإدارة</h1>
      <form method="post">
        <div class="mb-3">
          <label class="form-label">اسم المستخدم</label>
          <input type="text" name="username" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">كلمة المرور</label>
          <input type="password" name="password" class="form-control" required>
        </div>
        <button class="btn btn-dark w-100">دخول</button>
      </form>
    </div>
  </div>
</div>
</body>
</html>

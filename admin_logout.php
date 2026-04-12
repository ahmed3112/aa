<?php
require __DIR__ . '/helpers.php';

unset($_SESSION['admin_logged_in']);
flash('success', 'تم تسجيل الخروج.');
header('Location: /admin_login.php');
exit;

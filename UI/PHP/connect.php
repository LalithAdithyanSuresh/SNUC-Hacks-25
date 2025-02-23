<?php
function loadEnv($path) {
    if (!file_exists($path)) {
        throw new Exception(".env file not found");
    }

    $lines = file($path, FILE_IGNORE_NEW_LINES | FILE_SKIP_EMPTY_LINES);
    foreach ($lines as $line) {
        putenv($line);
    }
}

loadEnv(__DIR__ . '/.env');

$uri = getenv('DB_URI');
$fields = parse_url($uri);

$conn = "mysql:";
$conn .= "host=" . $fields["host"];
$conn .= ";port=" . $fields["port"];
$conn .= ";dbname=defaultdb";
$conn .= ";sslmode=verify-ca;sslrootcert=ca.pem";

try {
    $db = new PDO($conn, $fields["user"], $fields["pass"]);
    $stmt = $db->query("SELECT VERSION()");
    print($stmt->fetch()[0]);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}

?>
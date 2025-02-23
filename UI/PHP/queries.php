<?php

require 'connect.php';

header("Access-Control-Allow-Origin: *"); // Allow CORS if needed
header("Content-Type: application/json");

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    // Get JSON input
    $input = json_decode(file_get_contents("php://input"), true);
    
    echo json_encode(["message" => "Hello from PHP!", "data" => $input]);
} else {
    echo json_encode(["error" => "Invalid request method"]);
}
?>

var feedCheck = true;
var totalObjectFrequency = {}; // Stores cumulative object frequencies across frames


function Start() {
    feedCheck = true;
    document.getElementById("StopBttn").style.display = 'block';
    document.getElementById("StartBttn").style.display = 'none';
    detectObjects();
}
function Stop() {
    feedCheck = false;
    document.getElementById("StopBttn").style.display = 'none';
    document.getElementById("StartBttn").style.display = 'block';
}

async function startWebcam() {
    const video = document.getElementById("video");
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (error) {
        console.error("Error accessing webcam:", error);
    }
    detectObjects();
}

async function captureFrame() {
    const video = document.getElementById("video");
    const canvas = document.createElement("canvas");
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas.toDataURL("image/jpeg").split(",")[1]; // Convert to Base64
}

async function detectObjects() {
    const GOOGLE_VISION_API_KEY = "AIzaSyCyFi55AE8nKFwQakb2MzMkCLx6d1774uE";
    const ENDPOINT = `https://vision.googleapis.com/v1/images:annotate?key=${GOOGLE_VISION_API_KEY}`;

    const base64Image = await captureFrame();

    const payload = {
        requests: [
            {
                image: { content: base64Image },
                features: [{ type: "OBJECT_LOCALIZATION" }],
            },
        ],
    };

    try {
        const response = await fetch(ENDPOINT, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();
        const objectsDetected = data.responses[0]?.localizedObjectAnnotations?.map((obj) => obj.name) || [];

        // Create a dictionary for the current frame
        const currentFrameFrequency = {};
        objectsDetected.forEach(obj => {
            currentFrameFrequency[obj] = (currentFrameFrequency[obj] || 0) + 1;
        });

        // Update the total frequencies
        Object.keys(currentFrameFrequency).forEach(obj => {
            totalObjectFrequency[obj] = (totalObjectFrequency[obj] || 0) + currentFrameFrequency[obj];
        });

        console.log("Current Frame Objects:", currentFrameFrequency);
        console.log("Total Detected Objects (Cumulative):", totalObjectFrequency);

    } catch (error) {
        console.error("Error:", error);
    }

    if (feedCheck) {
        setTimeout(detectObjects, 300);
    }
}

// Start the webcam when the page loads
window.onload = startWebcam;

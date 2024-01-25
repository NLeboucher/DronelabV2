import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
//QQQQQQ
console.log("app.js")
// Three.js setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('scene-container').appendChild(renderer.domElement);

// Initialize OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);


const pointLight = new THREE.PointLight(0xffffff, 1, 100);
pointLight.position.set(0, 0, 50);
scene.add(pointLight);

// Create landmark points
const landmarkGeometry = new THREE.SphereGeometry(0.5, 32, 32);
const landmarkMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
const landmarks = {};
for (let i = 0; i < 33; i++) { // Assuming 33 landmarks
    const landmarkMesh = new THREE.Mesh(landmarkGeometry, landmarkMaterial);
    landmarkMesh.position.set(0, 0, 0);
    scene.add(landmarkMesh);
    landmarks[i] = landmarkMesh;
}

// Camera position
camera.position.z = 50;
const IP = "localhost"
let port = 8002;
// WebSocket connection
var ws = new WebSocket("ws://"+IP+":"+port+"/ws");
console.log(ws);

ws.onmessage = function(event) {
    const data = event.data.split(',');
    const id = parseInt(data[0]);
    const x = parseFloat(data[1])*25;
    const y = parseFloat(data[2])*25;
    const z = parseFloat(data[3])*25;
    console.log(id, x, y, z);
    if (landmarks[id]) {
        landmarks[id].position.set(x, y, z);
    }
};

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}
animate();
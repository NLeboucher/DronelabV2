import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// import { DragControls } from 'DragControls';
// import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

// import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
// import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
// import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
// import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'; 
// app.js
let scene, camera, renderer, points;
var landmarks = [];

function init() {
    // Create scene
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    scene.add(directionalLight);

    // Create points geometry
    const geometry = new THREE.BufferGeometry();
    const vertices = new Float32Array(landmarks.length * 3); // 3 coordinates for each landmark
    geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    const material = new THREE.PointsMaterial({ color: 0xff0000, size: 0.05 });
    points = new THREE.Points(geometry, material);
    scene.add(points);

    camera.position.z = 5;

    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);

    // Start the animation loop
    animate();
}

function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

function updateLandmarks(newLandmarks) {
    landmarks.splice(0, landmarks.length, ...newLandmarks);
    const vertices = new Float32Array(landmarks.flat());
    points.geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
    points.geometry.attributes.position.needsUpdate = true; // Inform Three.js to update the vertices
}

// Simulate receiving data from a WebSocket
const socket = new WebSocket('ws://localhost:8001'); // Change to your WebSocket server address
socket.onmessage = function(event) {
    const data = event.data.split(',').map(Number);
    if (data.length === 4) { // landmark_id, x, y, z
        updateLandmarks([data[1], data[2], data[3]]); // Push x, y, z to landmarks
    }
};

init();


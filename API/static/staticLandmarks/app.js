import * as THREE from 'three';
// import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
// import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
// import { DragControls } from 'DragControls';
// import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

// import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
// import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
// import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
// import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'; 
let scene, camera, renderer, points;
const landmarks = {};

init();
animate();

function init() {
    // Basic Three.js setup
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 5;
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);

    // Points material
    const material = new THREE.PointsMaterial({ color: 0x888888, size: 0.05 });

    // Create points for landmarks
    for (let i = 0; i < 33; i++) { // Assuming 33 landmarks
        const geometry = new THREE.BufferGeometry();
        geometry.setAttribute('position', new THREE.Float32BufferAttribute([0, 0, 0], 3));
        const point = new THREE.Points(geometry, material);
        scene.add(point);
        landmarks[i] = point;
    }

    // Handle window resize
    window.addEventListener('resize', onWindowResize, false);
    console.log("init done")

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
let port = 8001;
const IP = "localhost"
// WebSocket connection
const socket = new WebSocket("ws://"+IP+":" + port + "/ws");

socket.onmessage = function(event) {
    console.log("message received:")
    const data = event.data;
    console.log("data:",data)
    const match = data.match(/Landmark (\d+): X=([-\d.]+), Y=([-\d.]+), Z=([-\d.]+)/);
    console.log("match:",match)
    if (match) {
        const id = parseInt(match[1]);
        const x = parseFloat(match[2]);
        const y = parseFloat(match[3]);
        const z = parseFloat(match[4]);
        
        // Update landmark position
        if (landmarks[id]) {
            landmarks[id].geometry.attributes.position.setXYZ(0, x, y, z);
            landmarks[id].geometry.attributes.position.needsUpdate = true;
        }
    }
};

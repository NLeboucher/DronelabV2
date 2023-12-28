import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

// Scene, Camera, Renderer Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);
document.body.appendChild(renderer.domElement);

// Load the Background Texture
const textureLoader = new THREE.TextureLoader();
textureLoader.load('static/assets/equirectangular_bg.png', function (texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.background = texture;
});

// Lighting
const light = new THREE.AmbientLight(0xffffff, 3); // soft white light
light.position.set(0, 1, 1).normalize();
scene.add(light);

// add fog
// scene.fog = new THREE.FogExp2(0x000000, 0.6);

// OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);



// Drone Class
class Drone {
    constructor(id, position, model) {
        this.id = id;
        this.position = position;
        this.model = model.clone(); // Clone the model
        this.model.position.set(position.x, position.y, position.z);
        scene.add(this.model);
    }
}

// Load the Drone Model
const loader = new GLTFLoader();
let droneModel; // This will hold the original loaded model

loader.load('static/assets/drone.glb', (gltf) => {
    droneModel = gltf.scene;
    // add the model to the scene
    scene.add(droneModel);

    // Once the model is loaded, create drones
    createDrones();
});

function createDrones() {
    const drones = [];
    const N = 5; // Number of drones
    for (let i = 0; i < N; i++) {
        // const drone = new Drone(i, new THREE.Vector3(i * 0.5, 0, 0), droneModel);
        const random_position = new THREE.Vector3(
            Math.random() * 1 - 0.5,
            Math.random() * 1 - 0.5,
            Math.random() * 1 - 0.5
        );
        const drone = new Drone(i, random_position, droneModel);
        drones.push(drone);
    }
}

// Camera Position
camera.position.z = 2;

// Animation Loop
function animate() {
    requestAnimationFrame(animate);
    controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
    renderer.render(scene, camera);
}
animate();

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DragControls } from 'DragControls';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
// Drone Setup
const IP="172.21.73.34"
const apiUrl = `http://${IP}:8080/`;
const useTrueDrones = false;

// Scene, Camera, Renderer Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer();

renderer.setSize(window.innerWidth, window.innerHeight);
// renderer.domElement.setAttribute('draggable', 'true');
document.body.appendChild(renderer.domElement);

// Load the Background Texture
const textureLoader = new THREE.TextureLoader();
textureLoader.load('assets/equirectangular_bg.png', function (texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.background = texture;
});

// Lighting
const light = new THREE.AmbientLight(0xffffff, 3); // soft white light
light.position.set(0, 1, 1).normalize();
scene.add(light);

// create a wireframe box selection

const boxGeometry = new THREE.BoxGeometry(1, 1, 1);
const boxMaterial = new THREE.MeshBasicMaterial({
    color: 0xffff00,
    wireframe: true
});
const selectionBox = new THREE.Mesh(boxGeometry, boxMaterial);
selectionBox.visible = false; // Initially hidden
scene.add(selectionBox);

// add fog
// scene.fog = new THREE.FogExp2(0x000000, 0.6);

// OrbitControls
const controls = new OrbitControls(camera, renderer.domElement);



// Drone Class
class Drone {
    constructor(id, position, model) {
        this.id = id;
        this.URI = ""
        this.position = position;
        this.model = model.clone(); // Clone the model
        this.model.position.set(position.x, position.z, position.y);
        this.goalPosition = new THREE.Vector3(position.x, position.z, position.y);
        this.model.castShadow = true;
        this.model.receiveShadow = true;
        scene.add(this.model);
    }
    toString() {
        return `(id: ${this.id}, URI:${this.URI}): modelposition: ${this.model.position.x} /${this.position.x} , ${this.model.position.y} /${this.position.y}, ${this.model.position.z} /${this.position.z} `;
       }
}

// fetch(apiUrl)
//   .then(response => {
//     if (!response.ok) {
//       throw new Error('Network response was not ok');
//     }
//     else {
//         console.log("Connected to the API")
//     }
//     return response.json();
//   })
//   .then(data => {
//     // Display data in an HTML element
//     outputElement.textContent = JSON.stringify(data, null, 2);
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   });

// GUI
const gui = new GUI()
const cubeFolder = gui.addFolder('Drones')
// Load the Drone Model
const loader = new GLTFLoader();
let droneModel; // This will hold the original loaded model
const axesHelper = new THREE.AxesHelper( 5 );
scene.add( axesHelper );
let drones = [];
loader.load('assets/drone.glb', (gltf) => {
    droneModel = gltf.scene;
    console.log(droneModel)
    // add the model to the scene
    // scene.add(droneModel);

    // Once the model is loaded, create drones
    createDrones();
    

});

async function asyncCall(call="") {
    console.log('calling'+ useTrueDrones);
    if(useTrueDrones){
        fetch(apiUrl+call)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(data => {
    // Display data in an HTML element
    outputElement.textContent = JSON.stringify(data, null, 2);
  })
  .catch(error => {
    console.error('Error:', error);
  });
    console.log(result);
    }
    
    // Expected output: "resolved"
  }



function createDrones(N=5) {

    // const N = 5; // Number of drones
    for (let i = 0; i < N; i++) {
        const random_position = new THREE.Vector3(
            Math.random() * 3,
            Math.random() * 3,
            Math.random() * 3,
        );
        const drone = new Drone(i, random_position, droneModel);
        // console.log(drone.goalPosition.x,drone.goalPosition.y,drone.goalPosition.z)
        drones.push(drone);

        let SepcubeFolder = cubeFolder.addFolder('Drone '+i)
        SepcubeFolder.add(drone, 'id');
        SepcubeFolder.add(drone, 'URI');
        let PositionFolder = SepcubeFolder.addFolder('Position '+i)

        PositionFolder.add(drone.position, 'x');
        PositionFolder.add(drone.position, 'y');
        PositionFolder.add(drone.position, 'z');
        let GoalPositionFolder = SepcubeFolder.addFolder('Destination '+i)
        GoalPositionFolder.add(drone.goalPosition, 'x');
        GoalPositionFolder.add(drone.goalPosition, 'y');
        GoalPositionFolder.add(drone.goalPosition, 'z');
        // SepcubeFolder.add(drone.model.position, 'x');
        // SepcubeFolder.add(drone.model.position, 'y');
        // SepcubeFolder.add(drone.model.position, 'z');
        // SepcubeFolder.add(drone, 'model');
        // console.log(drone.toString())
        // const drone = new Drone(i, new THREE.Vector3(i * 0.5, 0, 0), droneModel);

        // const box = new THREE.BoxHelper( drone.model, 0xffff00 );
        // scene.add( box );

    }
}

// Camera Position
camera.position.z = 2;
async function updatePositions() {
    drones.forEach(item => {
        // console.log(item.toString())
        item.model.position.set(item.position.x, item.position.z, item.position.y);
    }); 
}


function animateDrones() {
    drones.forEach(drone => {
        // Assuming children 5 to 8 are the propellers
        for (let i = 5; i <= 8; i++) {
            let propeller = drone.model.children[0].children[i];
            let speed = 0.2;
            if(drone.position.z>0.0){
                propeller.rotation.z += speed;
            }
            if(drone.position.z<0.0){
                drone.position.z=0.0;
            }
            
        }
    });
}

var alpha = 0.000;
const alphaIncrement = 0.001; // Adjust this value for speed of interpolation

function InterpolateDroneMotion() {
    drones.forEach(drone => {
        if (!drone.position.equals(drone.goalPosition)&&drone.position.z>0.0) {
            // Interpolate towards the goal position
            drone.position.lerpVectors(drone.position, drone.goalPosition, alpha);
            // console.log("Interpolated Position", drone.id, ":", drone.position.x, drone.position.y, drone.position.z);
        }
    });

    alpha += alphaIncrement;
    if (alpha > 1) {
        alpha = 0; // Reset alpha if it exceeds 1
        // Optionally, update drone.goalPosition here if you want a continuous movement
    }
}
let f = 0;
let start=Date.now();
// Animation Loop
function animate() {
    f+=1;
    // console.log(Math.floor((Date.now()-start))/1000)
    if(Math.floor((Date.now()-start)/1000)>=1){
        console.log(f); 
        f=0;start=Date.now();
    }
    
    updatePositions();
    animateDrones();
    InterpolateDroneMotion();

    requestAnimationFrame(animate);
    controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
    renderer.render(scene, camera);

}
animate();




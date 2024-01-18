import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DragControls } from 'DragControls';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';

import { EffectComposer } from 'three/addons/postprocessing/EffectComposer.js';
import { RenderPass } from 'three/addons/postprocessing/RenderPass.js';
import { UnrealBloomPass } from 'three/addons/postprocessing/UnrealBloomPass.js';
import { OutputPass } from 'three/addons/postprocessing/OutputPass.js'; 

// Drone Setup
let IP="127.0.0.1"
let apiUrl = `http://${IP}:8080/`;
const useTrueDrones = false;
let DroneAPIConnected = false;
// Scene, Camera, Renderer Setup
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(90, window.innerWidth / window.innerHeight, 0.3, 1000);
const renderer = new THREE.WebGLRenderer();
camera.position.set(-5/3, -3/3, 0);
camera.lookAt(0, 0, 0);
renderer.setSize(window.innerWidth, window.innerHeight);
// renderer.domElement.setAttribute('draggable', 'true');
document.body.appendChild(renderer.domElement);

document.getElementById("ip").value = IP;

// Load the Background Texture
const textureLoader = new THREE.TextureLoader();
textureLoader.load('assets/equirectangular_bg.png', function (texture) {
    texture.mapping = THREE.EquirectangularReflectionMapping;
    scene.background = texture;
});

// For the post-processing
const composer = new EffectComposer(renderer);
const renderPass = new RenderPass(scene, camera);
const bloomPass = new UnrealBloomPass(
    new THREE.Vector2(window.innerWidth, window.innerHeight),
    0.4, // strength
    1.9, // radius
    5.5 // threshold
);
const outputPass = new OutputPass();

composer.addPass(renderPass);
composer.addPass(bloomPass);
composer.addPass(outputPass);

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

// add raycaster
const raycaster = new THREE.Raycaster();



// Drone Class
class Drone {
    static droneMeshes = [];
    constructor(id, position, model) {
        this.id = id;
        this.URI = ""
        this.position = position;
        console.log("model",model)
        this.model = model.clone(); // Clone the model
        this.model.position.set(position.x, position.z, position.y);
        this.goalPosition = new THREE.Vector3(position.x, position.z, position.y);
        this.model.castShadow = true;
        this.model.receiveShadow = true;
        this.model.layers.enable(1); // Enable layer 1 for the model
        scene.add(this.model);
        Drone.droneMeshes.push(this.model);
    }
    toString() {
        return `(id: ${this.id}, URI:${this.URI}): modelposition: ${this.model.position.x} /${this.position.x} , ${this.model.position.y} /${this.position.y}, ${this.model.position.z} /${this.position.z} `;
       }
}

// Plan on the background
const worldWidth = 256, worldDepth = 256;
const geometry = new THREE.PlaneGeometry(20000, 20000, worldWidth - 1, worldDepth - 1);

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
let axesHelper = new THREE.AxesHelper( 5 );
scene.add( axesHelper );
let drones = [];
function loadDroneModel() {
    loader.load('assets/drone.glb', (gltf) => {
        droneModel = gltf.scene;
        // add the model to the scene
        // scene.add(droneModel);
        // Once the model is loaded, create drones
        if(!useTrueDrones){
            createScene(document.getElementById("NDrones").value=== "NDrones" ? 1 : document.getElementById("NDrones").value);
        }
        else{
            createScene();
        }
        console.log("loaded model")
    });
}
loadDroneModel()
const controls = new DragControls( Drone.droneMeshes, camera, renderer.domElement );   
// controls.addEventListener( 'dragstart', dragStartCallback );
// controls.addEventListener( 'dragend', dragendCallback );


async function asyncCall(call="") {
    console.log('calling API : '+ `http://${IP}:8000/`);
    const response = await fetch(`http://${IP}:8000/`);
    const ok = await response.json();
    console.log(ok);
    return ok;
}
// async function asyncCall(call="") {
//     console.log('calling API : '+ useTrueDrones + ''+apiUrl+call);

//     if(useTrueDrones){
//         fetch(URL=apiUrl+call)
//   .then(response => {
//     console.log("api response" ,response)
//     if (!response.ok) {
//       throw new Error('Network response was not ok');
//     }else{
//         DroneAPIConnected=true;
//         console.log("Connected to the API")
//     }
//     console.log("api response" ,response)
//     return response.json();
//     console.log("api response" ,response)
//   })
//   .then(data => {
//     // Display data in an HTML element
//     outputElement.textContent = JSON.stringify(data, null, 2);
//   })
//   .catch(error => {
//     console.error('Error:', error);
//   });
//     console.log(result);
//     }
    
//     // Expected output: "resolved"
//   }


  function clearScene() {
    while (scene.children.length > 0) { 
        let child = scene.children[0];
    
        if (child.geometry) {
            child.geometry.dispose(); 
        }
    
        if (child.material) {
            // In case of multi-materials, dispose all of them
            if (Array.isArray(child.material)) {
                for (const material of child.material) {
                    material.dispose();
                }
            } else {
                child.material.dispose();
            }
        }
    
        scene.remove(child); 
    }
};
function createScene(N=1) {
    drones=[]; // Reset the drones array
    axesHelper = new THREE.AxesHelper( 5 );
    scene.add( axesHelper );
    // const N = 5; // Number of drones
    for (let i = 0; i < N; i++) {
        const random_position = new THREE.Vector3(
            Math.random() * 1.5,
            Math.random() * 0.5,
            Math.random() * 0.5 ,
        );
        const drone = new Drone(i, random_position, droneModel);
        // console.log(drone.goalPosition.x,drone.goalPosition.y,drone.goalPosition.z)
        drones.push(drone);
        Drone.droneMeshes.push(drone.model);

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
        // console.log(item.worldPosition);
        // item.model.position.set(item.worldPosition.x, item.worldPosition.z,item.worldPosition.y);
    }); 
}
async function updateRealPositions() {
    const ans = await asyncCall("/getestimatedpositions/")
    if(ans.length>0){
        drones.forEach(item => {
            // console.log(item.toString())
            item.position = ans[0],ans[1],ans[2];
            // console.log(item.worldPosition);
            // item.model.position.set(item.worldPosition.x, item.worldPosition.z,item.worldPosition.y);
        });
        console.log("updated positions")
    }
    else{
        if(DroneAPIConnected){
        console.log("no positions")
    }
}
}
// Drag Controls    
controls.addEventListener('drag', function(event) {
       
    console.log("Dragging:",event.object.position,drones[0].model.position,drones[0].position)
});
controls.addEventListener('dragstart', function(event) {
    console.log("raycaster",raycaster)
    const intersects = raycaster.intersectObjects(Drone.droneMeshes, false);
    // const draggedDrone = event.object;
    const droneIndex = intersects.id;
    console.log("Dragging START:",event.object.position,drones[0].model.position,drones[0].position)

    if (droneIndex !== -1) {
        console.log('DRONE:', droneIndex);
        // You can now work with the specific drone
        // For example, drones[droneIndex].position, or any other property
    }
});
controls.addEventListener('dragend', function(event) {
    // drones.forEach((child) => {
    //     var worldPosition = new THREE.Vector3();
    //     var b = new THREE.Vector3();
    //     child.getWorldPosition(worldPosition);
    //     let a = child.worldToLocal(b);
    //     console.log('Child ID:', child.id, 'World Position:', worldPosition, 'Local Position:', a,b);
    // });
    updatePositions();
    updateRealPositions();
});

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
    // controls.update(); // Only required if controls.enableDamping or controls.autoRotate are set to true
    renderer.render(scene, camera);

    composer.render()

}
animate();


document.addEventListener('DOMContentLoaded',  function() {
    document.getElementById('button1').addEventListener('click', showIPValue);
});


document.getElementById("NDrones").addEventListener("change", function () {
    clearScene();

loadDroneModel();



});

async function showIPValue() {
    console.log("API connection ... ");
    IP = document.getElementById("ip").value;
    apiUrl = `http://${IP}:8080/`
    let a = await asyncCall() ;
    console.log("API answer",a);
    const useTrueDrones = a=== "API Connected";
    if(useTrueDrones){
        document.getElementById('button1').innerText = "API Connected";
    }
    else{
        document.getElementById('button1').innerText = "API Not Connected";
    }
    console.log( useTrueDrones? "API Connected" : "API Not Connected");
}

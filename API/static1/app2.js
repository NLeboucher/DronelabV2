import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { DragControls } from 'DragControls';
import { GUI } from 'three/addons/libs/lil-gui.module.min.js';
var scene = new THREE.Scene();
scene.background = new THREE.Color( 0xf0f0f0 );
var camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 1, 10000 );
var objects = [];

var renderer = new THREE.WebGLRenderer();
renderer.setSize( window.innerWidth, window.innerHeight );
document.body.appendChild( renderer.domElement );

camera.position.z = 1000;

var startColor;

function init() {
	scene.add( new THREE.AmbientLight( 0x0f0f0f ) );

	var light = new THREE.SpotLight( 0xffffff, 1.5 );
	light.position.set( 0, 500, 2000 );

	scene.add(light);


	for (var i = 0; i < 100; i++) {
		var object = droneModel.clone();

		object.position.x = Math.random() * 1000 - 500;
		object.position.y = Math.random() * 600 - 300;
		object.position.z = Math.random() * 800 - 400;

		object.castShadow = true;
		object.receiveShadow = true;
        console.log("object :", object)
		scene.add( object );

		objects.push( object );
	}

	var controls = new DragControls( objects, camera, renderer.domElement );
	controls.addEventListener( 'dragstart', dragStartCallback );
	controls.addEventListener( 'dragend', dragendCallback );
}
const loader = new GLTFLoader();
let droneModel;
loader.load('assets/drone.glb', (gltf) => {
    droneModel = gltf.scene;
    
    // droneModel.setSize(100, 100);
    // groupDroneModel = new THREE.Group();
    // groupDroneModel.add(droneModel);
    console.log("group :", droneModel)
    // add the model to the scene
    // scene.add(droneModel);
    init();
animate();
});


function dragStartCallback(event) {
	startColor = event.object.material.color.getHex();
	event.object.material.color.setHex(0x000000);
}

function dragendCallback(event) {
	event.object.material.color.setHex(startColor);
}

function animate() {
	requestAnimationFrame( animate );

	renderer.render(scene, camera);
};

animate();



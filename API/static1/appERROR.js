import * as THREE from 'three';

import Stats from 'three/addons/libs/stats.module.js';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';

import { SelectionBox } from 'three/addons/interactive/SelectionBox.js';
import { SelectionHelper } from 'three/addons/interactive/SelectionHelper.js';

let container, stats;
let camera, scene, renderer;
let helper;
let selectionBox;
const loader = new GLTFLoader();
let droneModel;
let droneModelGeometry = new THREE.Group();
function init() {

    container = document.createElement( 'div' );
    document.body.appendChild( container );

    camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.1, 500 );
    camera.position.z = 50;
    // camera.lookAt(new THREE.Vector3(0, 0, 0)); // Assuming (0, 0, 0) is the center of your scene

    scene = new THREE.Scene();
    scene.background = new THREE.Color( 0xf0f0f0 );

    scene.add( new THREE.AmbientLight( 0xaaaaaa ) );

    const light = new THREE.SpotLight( 0xffffff, 10000 );
    light.position.set( 0, 25, 50 );
    light.angle = Math.PI / 5;

    light.castShadow = true;
    light.shadow.camera.near = 10;
    light.shadow.camera.far = 100;
    light.shadow.mapSize.width = 1024;
    light.shadow.mapSize.height = 1024;

    scene.add( light );

    const geometry = new THREE.RingGeometry();

    for ( let i = 0; i < 2; i ++ ) {
        console.log("droneModel :", droneModel)
        let group 
        // let inputed = droneModel.children[0];
        // console.log("droneModel inputed :", inputed)
        let object2 = new THREE.Mesh( geometry, new THREE.MeshLambertMaterial( { color: Math.random() * 0xffffff } ) );
        // let object = new THREE.Mesh(inputed, new THREE.MeshLambertMaterial( { color: Math.random() * 0xffffff } ) );
        let object = object2;
        // object.setValues(droneModel);
        console.log("object :", object)
        object.position.x = Math.random() * 80 - 40;
        object.position.y = Math.random() * 45 - 25;
        object.position.z = Math.random() * 45 - 25;
        // object.position.x = Math.random() * 10 - 40;
        // object.position.y = Math.random() * 45 - 25;
        // object.position.z = Math.random() * 45 - 25;

        object.rotation.x = Math.random() * 2 * Math.PI;
        object.rotation.y = Math.random() * 2 * Math.PI;
        object.rotation.z = Math.random() * 2 * Math.PI;
        let r = Math.random();
        object.scale.x = r;
        object.scale.y = r;
        object.scale.z = r;

        object.castShadow = true;
        object.receiveShadow = true;

        scene.add( object );
        selectionBox = new SelectionBox( camera, scene );


    }

    renderer = new THREE.WebGLRenderer( { antialias: true } );
    renderer.setPixelRatio( window.devicePixelRatio );
    renderer.setSize( window.innerWidth, window.innerHeight );
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFShadowMap;

    container.appendChild( renderer.domElement );

    stats = new Stats();
    container.appendChild( stats.dom );

    window.addEventListener( 'resize', onWindowResize );
    helper = new SelectionHelper( renderer, 'selectBox' );
    animate();
}
loader.load('assets/drone.glb', (gltf) => {
    droneModel = gltf.scene;
    // droneModel.setSize(100, 100);
    // groupDroneModel = new THREE.Group();
    // groupDroneModel.add(droneModel);
    // console.log("group :", droneModel.children[0])
    // add the model to the scene
    // scene.add(droneModel);
    // for (let i = 0; i <= 8; i++) {
    //     droneModelGeometry.add(droneModel.children[0].children[i]);
    // }
    // droneModelGeometry = droneModel.children[0].children.geometry;
    init();
});





function onWindowResize() {

    camera.aspect = window.innerWidth / window.innerHeight;
    console.log("camera",camera)
    camera.updateProjectionMatrix();

    renderer.setSize( window.innerWidth, window.innerHeight );

}

//

function animate() {

    requestAnimationFrame( animate );

    render();
    stats.update();

}

function render() {

    renderer.render( scene, camera );

}

selectionBox = new SelectionBox( camera, scene );


document.addEventListener( 'pointerdown', function ( event ) {
    
    for ( const item of selectionBox.collection ) {
        console.log("selection : ",item);
        item.material.emissive.set( 0x000000 );
    }

    selectionBox.startPoint.set(
        ( event.clientX / window.innerWidth ) * 2 - 1,
        - ( event.clientY / window.innerHeight ) * 2 + 1,
        0.5 );

} );

document.addEventListener( 'pointermove', function ( event ) {

    if ( helper.isDown ) {

        for ( let i = 0; i < selectionBox.collection.length; i ++ ) {

            selectionBox.collection[ i ].material.emissive.set( 0x1232f );

        }

        selectionBox.endPoint.set(
            ( event.clientX / window.innerWidth ) * 2 - 1,
            - ( event.clientY / window.innerHeight ) * 2 + 1,
            0.5 );

        const allSelected = selectionBox.select();

        for ( let i = 0; i < allSelected.length; i ++ ) {

            allSelected[ i ].material.emissive.set( 0xffffff );

        }

    }

} );

document.addEventListener( 'pointerup', function ( event ) {

    selectionBox.endPoint.set(
        ( event.clientX / window.innerWidth ) * 2 - 1,
        - ( event.clientY / window.innerHeight ) * 2 + 1,
        0.5 );

    const allSelected = selectionBox.select();

    for ( let i = 0; i < allSelected.length; i ++ ) {

        allSelected[ i ].material.emissive.set( 0x1232f );

    }

} );
import * as THREE from 'three';

			import { DragControls } from 'three/addons/controls/DragControls.js';
            import { GUI } from 'three/addons/libs/lil-gui.module.min.js';


			let container;
			let camera, scene, renderer;
			let controls, group;
			let enableSelection = false;

			const objects = [];

			const mouse = new THREE.Vector2(), raycaster = new THREE.Raycaster();

            
            let gui; // GUI variable
            let selectedObject = null; // Variable to hold the currently selected object

            let positionFolder;
			init();

			function init() {
                    // Initialize GUI
                gui = new GUI();
                positionFolder = gui.addFolder('Position');
                gui.hide(); // Initially hide the GUI
				container = document.createElement( 'div' );
				document.body.appendChild( container );

				camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.1, 500 );
				camera.position.z = 25;

				scene = new THREE.Scene();
				scene.background = new THREE.Color( 0xf0f0f0 );

				scene.add( new THREE.AmbientLight( 0xaaaaaa ) );

				const light = new THREE.SpotLight( 0xffffff, 10000 );
				light.position.set( 0, 25, 50 );
				light.angle = Math.PI / 9;

				light.castShadow = true;
				light.shadow.camera.near = 10;
				light.shadow.camera.far = 100;
				light.shadow.mapSize.width = 1024;
				light.shadow.mapSize.height = 1024;

				scene.add( light );

				group = new THREE.Group();
				scene.add( group );

				const geometry = new THREE.BoxGeometry();

				for ( let i = 0; i < 200; i ++ ) {

					const object = new THREE.Mesh( geometry, new THREE.MeshLambertMaterial( { color: Math.random() * 0xffffff } ) );

					object.position.x = Math.random() * 30 - 15;
					object.position.y = Math.random() * 15 - 7.5;
					object.position.z = Math.random() * 20 - 10;

					object.rotation.x = Math.random() * 2 * Math.PI;
					object.rotation.y = Math.random() * 2 * Math.PI;
					object.rotation.z = Math.random() * 2 * Math.PI;

					object.scale.x = Math.random() * 2 + 1;
					object.scale.y = Math.random() * 2 + 1;
					object.scale.z = Math.random() * 2 + 1;

					object.castShadow = true;
					object.receiveShadow = true;

					scene.add( object );

					objects.push( object );

				}

				renderer = new THREE.WebGLRenderer( { antialias: true } );
				renderer.setPixelRatio( window.devicePixelRatio );
				renderer.setSize( window.innerWidth, window.innerHeight );
				renderer.shadowMap.enabled = true;
				renderer.shadowMap.type = THREE.PCFShadowMap;

				container.appendChild( renderer.domElement );

				controls = new DragControls( [ ... objects ], camera, renderer.domElement );
				controls.addEventListener( 'drag', render );
				controls.addEventListener('drag', function() {
					group.children.forEach((child) => {
						var worldPosition = new THREE.Vector3();
						var b = new THREE.Vector3();
						child.getWorldPosition(worldPosition);
						let a = child.worldToLocal(b);
						console.log('Child ID:', child.id, 'World Position:', worldPosition, 'Local Position:', a,b);
					});
				});

				//

				window.addEventListener( 'resize', onWindowResize );

				document.addEventListener( 'click', onClick );
				window.addEventListener( 'keydown', onKeyDown );
				window.addEventListener( 'keyup', onKeyUp );

				render();

			}
            function updateGUI() {
                // positionFolder.removeFolder(); // Remove the previous folder (if present)
                
                if (selectedObject) {
                    gui.show(); // Show the GUI when an object is selected
                    console.log("selectedObject",selectedObject)
                    console.log("positionFolder",positionFolder)
                    // positionFolder.clear(); // Clear previous GUI entries
                    if (positionFolder.folders){console.log("folders",positionFolder.folders)}
                    let child = positionFolder.addFolder('Position'+selectedObject.id);
                    // Add GUI controls to display and manipulate the position of the selected object
                    positionFolder.add(selectedObject.position, 'x', -30, 30).listen();
                    positionFolder.add(selectedObject.position, 'y', -15, 15).listen();
                    positionFolder.add(selectedObject.position, 'z', -20, 20).listen();
                } else {
                    gui.hide(); // Hide the GUI if no object is selected
                }
            }
			function onWindowResize() {

				camera.aspect = window.innerWidth / window.innerHeight;
				camera.updateProjectionMatrix();

				renderer.setSize( window.innerWidth, window.innerHeight );

				render();

			}

			function onKeyDown( event ) {

				enableSelection = ( event.keyCode === 16 ) ? true : false;

			}

			function onKeyUp() {

				enableSelection = false;

			}

			function onClick( event ) {

				event.preventDefault();

				if ( enableSelection === true ) {

					const draggableObjects = controls.getObjects();
					draggableObjects.length = 0;

					mouse.x = ( event.clientX / window.innerWidth ) * 2 - 1;
					mouse.y = - ( event.clientY / window.innerHeight ) * 2 + 1;

					raycaster.setFromCamera( mouse, camera );

					const intersections = raycaster.intersectObjects( objects, true );
                    
					if ( intersections.length > 0 ) {
                        
						const object = intersections[ 0 ].object;
                        selectedObject = object; // Update the selected object
                        updateGUI(); // Update the GUI with the new selection
						if ( group.children.includes( object ) === true ) {

							object.material.emissive.set( 0x000000 );
							scene.attach( object );

						} else {

							object.material.emissive.set( 0xaaaaaa );
							group.attach( object );

						}

						controls.transformGroup = true;
						draggableObjects.push( group );

                        // console.log("controled object position",intersections)

					}else{
                        selectedObject =null;
                        gui.destroy();
                        // console.log("controls",group.children)
						

                    }

					if ( group.children.length === 0 ) {

						controls.transformGroup = false;
						draggableObjects.push( ...objects );
                        
					}

				}
                // console.log("groupchilden",group,group.children.length,group.children[0].position)
				// for ( let i = 0; i < group.children.length; i ++ ) {
				// 	console.log("controled object position",group.children[i].transformGroup)
				// }
				
				render();

			}
			
			function render() {

				renderer.render( scene, camera );

			}
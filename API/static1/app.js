import * as THREE from 'three';

			import Stats from 'three/addons/libs/stats.module.js';
			import { DragControls } from 'three/addons/controls/DragControls.js';

			import { SelectionBox } from 'three/addons/interactive/SelectionBox.js';
			import { SelectionHelper } from 'three/addons/interactive/SelectionHelper.js';

			let container, stats;
			let camera, scene, renderer;
            const objects = [];
            let controls, group;
			let enableSelection = false;
            const mouse = new THREE.Vector2(), raycaster = new THREE.Raycaster();
            let selectedObject = null; // Variable to hold the currently selected object

			init();
			animate();

			function init() {

				container = document.createElement( 'div' );
				document.body.appendChild( container );

				camera = new THREE.PerspectiveCamera( 70, window.innerWidth / window.innerHeight, 0.1, 500 );
				camera.position.z = 50;

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

				const geometry = new THREE.BoxGeometry( 1, 1, 1 );

				for ( let i = 0; i < 200; i ++ ) {

					const object = new THREE.Mesh( geometry, new THREE.MeshLambertMaterial( { color: Math.random() * 0xffffff } ) );

					object.position.x = Math.random() * 80 - 40;
					object.position.y = Math.random() * 45 - 25;
					object.position.z = Math.random() * 45 - 25;

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

				stats = new Stats();
				container.appendChild( stats.dom );
                group = new THREE.Group();
                scene.add( group );
				window.addEventListener( 'resize', onWindowResize );
                controls = new DragControls( [ ... objects ], camera, renderer.domElement );
				controls.addEventListener( 'drag', render );
				controls.addEventListener('drag', function() {
					objects.children.forEach((child) => {
						var worldPosition = new THREE.Vector3();
						var b = new THREE.Vector3();
						child.getWorldPosition(worldPosition);
						let a = child.worldToLocal(b);
						console.log('Child ID:', child.id, 'World Position:', worldPosition, 'Local Position:', a,b);
					});
				});
                document.addEventListener( 'click', onClick );
				window.addEventListener( 'keydown', onKeyDown );
				window.addEventListener( 'keyup', onKeyUp );
                window.addEventListener( 'resize', onWindowResize );

				render();

			}

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


			function onWindowResize() {

				camera.aspect = window.innerWidth / window.innerHeight;
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

			const selectionBox = new SelectionBox( camera, scene );
			const helper = new SelectionHelper( renderer, 'selectBox' );

			document.addEventListener( 'pointerdown', function ( event ) {

				for ( const item of selectionBox.collection ) {

					item.material.emissive.set( 0x000000 );

				}

				selectionBox.startPoint.set(
					( event.clientX / window.innerWidth ) * 2 - 1,
					- ( event.clientY / window.innerHeight ) * 2 + 1,
					0.5 );

			} );

			document.addEventListener( 'pointermove', function ( event ) {

				if ( helper.isDown && enableSelection ===false ) {

					for ( let i = 0; i < selectionBox.collection.length; i ++ ) {

						selectionBox.collection[ i ].material.emissive.set( 0x000000 );

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
				console.log("selectionBox",selectionBox.collection)
			} );

			document.addEventListener( 'pointerup', function ( event ) {
                if(enableSelection === false){
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
            
                        if ( group.children.includes( object ) === true ) {
            
                            object.material.emissive.set( 0x000000 );
                            scene.attach( object );
            
                        } else {
            
                            object.material.emissive.set( 0xaaaaaa );
                            group.attach( object );
            
                        }
            
                        controls.transformGroup = true;
                        draggableObjects.push( group );
            
                    }
            
                    if ( group.children.length === 0 ) {
            
                        controls.transformGroup = false;
                        draggableObjects.push( ...objects );
            
                    }
                    console.log("group",group.children)
                }
            
                render();
            
            }

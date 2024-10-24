# DronelabV2
The reboot of the DVIC repo Dronelab using Crazyfly drones.

Here we use the cflib to control the drones. A framework with a higer learning rate to quickly develop. 

Our Solution works with an asynchronous API to controll our drones. 

```mermaid
graph TD
  subgraph API
    subgraph swarmcontrol.py
      A((SwarmControl))
      B[OpenLinks]
      C[CloseLinks]
      D[All_TakeOff]
      E[All_Land]
      F[All_GetEstimatedPositions]
      G[All_StartLinearMotion]
      H[All_MoveDistance]
    end
    subgraph helpers
      subgraph logger.py
        I((Logger))
      end
      subgraph move.py
        J((Move))
      end
      subgraph option.py
        K((Option))
      end

      subgraph Quad.py
        M((Quad))
      end
    end
    subgraph main.py
      O[OpenLinks]
      P[CloseLinks]
      Q[All_TakeOff]
      R[All_Land]
      S[All_GetEstimatedPositions]
      T[All_StartLinearMotion]
      U[All_MoveDistance]
    end
  end
  A --> B
  A --> C
  A --> D
  A --> E
  A --> F
  A --> G
  A --> H
  I --> A
  J --> A
  K --> A
  M --> A
  B --> O
  C --> P
  D --> Q
  E --> R
  F --> S
  G --> T 
  H --> U
```

We added here an example using the famous boids flock control algorithm, anther repo uses this framework using unity machine learning agents


```mermaid
graph TD
  subgraph boids
    subgraph swarmcontrol.py
        A[OpenLinks]
        B[CloseLinks]
        C[All_TakeOff]
        D[All_Land]
        E[All_GetEstimatedPositions]
        F[All_StartLinearMotion]
        G[All_MoveDistance]
    end
    H((MoveBoids))
    A <--> H
    B <--> H
    C <--> H
    D <--> H
    E <--> H
    F <--> H
    G <--> H

    
  end

```
# Get started
## Requirements
~~~
python3.10 here using 3.10.12
~~~
install virtualenv if you dont have it:

~~~
python3.10 -m pip install virtualenv 

~~~

clone the repository
~~~ 
git clone git@github.com:NLeboucher/DronelabV2.git
~~~
activate the virtual env from the root of the project
~~~
cd DRONELABV2
python3.10 -m virtualenv venv
sudo apt install python3.10-venv
source venv/bin/activate
~~~
install the python dependencies
~~~
pip install cflib pygame fastapi uvicorn mediapipe opencv-python pyrealsense tqdm jinja2
~~~

Now you have all the depedencies
## Use the framework
use the API/SwarmController with High Level methods to controll drones in a swarm

## Run the API
./runserverController

# Credits
boids_py from [Nathan Plamondon](https://github.com/meznak/boids_py), an implementation of Craig Reynolds' [Boids](https://www.red3d.com/cwr/boids/) in python using pygame.

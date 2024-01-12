using System.Collections;
using System.Collections.Generic;
using TMPro;
using UnityEngine;
using static DroneBehavior;

public class DroneSwarmControle : MonoBehaviour
{
    [SerializeField] private GameObject DronePrefab; // Référence au prefab du drone
    private int numberOfDrones = 0; // Nombre de drones à créer

    [SerializeField] private bool APIRequest = false;
    [SerializeField] private bool APITakeOff = false;
    [SerializeField] private bool droneAPITracking = false;
    [SerializeField] private bool droneAPIVelocity = false;
    [SerializeField] private bool StartGoTO = false;
    [SerializeField] private Vector3 GoToPosition = new Vector3(0, 0, 0);


    private List<GameObject> droneObjects = new List<GameObject>(); // Liste pour stocker les GameObjects des drones

    public static bool droneConected = false;
    public static List<DroneInformation> droneInformation = null; // Liste pour stocker les informations des drones
    [HideInInspector]
    public static int selectedDroneIndex = -1; // -1 means no selection
    public static DroneInformation selectedDrone = null; // This will be set to the selected drone

    public static bool droneInitialized = false;

    #region coroutine variables
    public static bool isCoroutineCheckDroneConnectionRunning = false;
    public static bool isCoroutineGetFromAPIRunning = false;
    public static bool isCoroutineTakeOffRunning = false;
    public static bool isCoroutineLandRunning = false;
    public static bool isCoroutineCloseLinksRunning = false;
    public static bool isCoroutineSetVelocity = false;
    #endregion

    //maxspeed of drone
    public float maxSpeed = 0.5f;
    public float closeEnoughDistance = 0.5f;
    private void Update()
    {

        TakOffAndLandManagement();

        ControlAPI();

        SetVelocity();





        if (droneConected == true && droneInformation != null && droneInformation.Count > 0 && droneInitialized == false && droneInformation[0].dronePosition.positionInfo)
        {
            InitialiserDrone();
        }
        // Si vous ne voulez pas utiliser l'API, vous pouvez simplement appeler la méthode UpdateDroneInfo() ici
        if (droneAPITracking)
        {
            if (droneObjects.Count > 0)
            {
                for (int i = 0; i < droneInformation.Count; i++)
                {
                    droneObjects[i].GetComponent<DroneBehavior>().UpdateDroneInfo(droneInformation[i]);
                    droneObjects[i].transform.position = new Vector3(droneInformation[i].dronePosition.positionDroneX, droneInformation[i].dronePosition.positionDroneZ, droneInformation[i].dronePosition.positionDroneY);
                    droneObjects[i].transform.rotation = Quaternion.Euler(0, droneInformation[i].dronePosition.rotationDroneYaw, 0);  
                    
                }
            }
        }
        // what drone did you select ?
        if (DroneSwarmControle.selectedDroneIndex >= 0 && DroneSwarmControle.selectedDroneIndex < DroneSwarmControle.droneInformation.Count)
        {
            selectedDrone = DroneSwarmControle.droneInformation[DroneSwarmControle.selectedDroneIndex];
            
        }

        if (StartGoTO && selectedDrone!=null && droneConected == true && droneInformation != null && droneInformation.Count > 0)
        {
            UpdateDroneVelocityTowardsGoTo( selectedDrone,  GoToPosition,  maxSpeed);
        }
        else
        {
            StartGoTO = false;
        }

    }

    //
    void ControlAPI()
    {
        if (APIRequest)
        {
            if (droneConected == false && !isCoroutineCheckDroneConnectionRunning)
            {
                StartCoroutine(APIHelper.CheckDroneConnection());
            }
            else if (droneConected == true && !isCoroutineGetFromAPIRunning)
            {
                StartCoroutine(APIHelper.GetFromAPI());
            }
        }
        else if (droneConected == true && !isCoroutineCheckDroneConnectionRunning && !isCoroutineGetFromAPIRunning && !isCoroutineCloseLinksRunning)
        {
            StartCoroutine(APIHelper.CloseLinks());
        }
        // Le cas où vous ne voulez pas utiliser l'API ou appeler InitialiserDrone() pourrait être traité ici
    }

    void InitialiserDrone()
    {
        droneInitialized = true;
        numberOfDrones = droneInformation.Count;
        for (int i = 0; i < numberOfDrones; i++)
        {
            Vector3 posDrone = new Vector3(droneInformation[i].dronePosition.positionDroneX, droneInformation[i].dronePosition.positionDroneZ, droneInformation[i].dronePosition.positionDroneY);
            Vector3 rotDrone = new Vector3(0, droneInformation[i].dronePosition.rotationDroneYaw, 0);

            Quaternion rotationQuaternion = Quaternion.Euler(rotDrone); // Convertit les angles Euler en Quaternion

            GameObject drone = Instantiate(DronePrefab, posDrone, rotationQuaternion);

            droneObjects.Add(drone);
            drone.GetComponent<DroneBehavior>().Initialiser(droneInformation[i]);
        }
    }

    void TakOffAndLandManagement()
    {
        if (APITakeOff)
        {
            if (droneConected && droneInformation != null && droneInformation.Count > 0 && droneInformation[0].takeoff == false && !isCoroutineTakeOffRunning )
            {
                Debug.Log("takeoff");
                StartCoroutine(APIHelper.TakeOff());
            }

           
        }

        else if (!APITakeOff)
        {
            if (droneConected  && droneInformation != null && droneInformation.Count > 0 && droneInformation[0].takeoff  && !isCoroutineLandRunning)
            {
                StartCoroutine(APIHelper.Land());
                APITakeOff = false;
            }
        }



    }



    public void SetVelocity()
    {
        if (droneAPIVelocity && droneConected && droneInformation != null && droneInformation.Count > 0 && droneInformation[0].takeoff && !isCoroutineSetVelocity)
        {
            StartCoroutine(APIHelper.SetVelocityToAPI());
        }

        
    }

    void UpdateDroneVelocityTowardsGoTo(DroneInformation selectedDrone, Vector3 GoToPosition, float maxSpeed)
    {
        if (selectedDrone == null)
            return;

        // Get the current position of the drone from its DroneInformation
        Vector3 dronePosition = new Vector3(
            selectedDrone.dronePosition.positionDroneX,
            selectedDrone.dronePosition.positionDroneY,
            selectedDrone.dronePosition.positionDroneZ
        );

        // Calculate the direction towards the target position
        Vector3 directionToTarget = (GoToPosition - dronePosition);

        // Check if the drone is close enough to the target position
        if (directionToTarget.magnitude < closeEnoughDistance)
        {
            // Stop the drone if it is close enough to the target
            selectedDrone.droneVelocity.vitesseDroneX = 0;
            selectedDrone.droneVelocity.vitesseDroneY = 0;
            selectedDrone.droneVelocity.vitesseDroneZ = 0;
            StartGoTO = false;
        }
        directionToTarget = directionToTarget.normalized;
        //if the direction vector is a local vector add this : 

        /*// Calculate the direction towards the target position
        Vector3 directionToTarget = (targetPosition - dronePosition);

        // Convert the direction to the drone's local space
        Vector3 directionToLocalSpace = droneRotation.Inverse() * directionToTarget;
        Vector3 desiredVelocityLocal = directionToLocalSpace.normalized * maxSpeed;*/


        // Scale the direction vector to the maximum speed
        Vector3 desiredVelocity = directionToTarget * maxSpeed ;

        // Update the drone's velocity in DroneInformation
        selectedDrone.droneVelocity.vitesseDroneX = desiredVelocity.x;
        selectedDrone.droneVelocity.vitesseDroneY = desiredVelocity.y;
        selectedDrone.droneVelocity.vitesseDroneZ = desiredVelocity.z;
    }
}
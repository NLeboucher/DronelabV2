using System.Collections;
using System.Collections.Generic;

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
    public float maxSpeed = 0.2f;
    public float closeEnoughDistance = 0.2f;
    private void Update()
    {

        TakOffAndLandManagement();

        ControlAPI();

        SetVelocity();





        if (droneConected == true && droneInformation != null && droneInformation.Count > 0 && !droneInitialized  && droneInformation[0].dronePosition.positionInfo)
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
        if (droneInformation != null && selectedDroneIndex >= 0 && selectedDroneIndex < droneInformation.Count)
        {
            selectedDrone = droneInformation[selectedDroneIndex];
        }
        else
        {
            selectedDrone = null; // Reset to null if conditions are not met
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

            if (selectedDrone != null)
            {
                if (selectedDrone.droneVelocity.vitesseDroneX == 0 && selectedDrone.droneVelocity.vitesseDroneY == 0 && selectedDrone.droneVelocity.vitesseDroneZ == 0)
                {
                    droneAPIVelocity = false;
                }
            }
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

        // Assume droneRotation is in Euler angles and convert it to a Quaternion
        Quaternion droneRotation = Quaternion.Euler(
            0,
            selectedDrone.dronePosition.rotationDroneYaw,
            0
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
            StartCoroutine(APIHelper.SetVelocityToAPI());
            StartGoTO = false;
            return; // Exit the function as no further calculation is needed
        }
        directionToTarget = (GoToPosition - dronePosition).normalized;

        // Convert the direction to the drone's local space
        Vector3 directionToLocalSpace = Quaternion.Inverse(droneRotation) * directionToTarget;

        // Scale the direction vector to the maximum speed
        Vector3 desiredVelocityLocal = directionToLocalSpace.normalized * maxSpeed;

        // Update the drone's velocity in DroneInformation
        selectedDrone.droneVelocity.vitesseDroneX = desiredVelocityLocal.x;
        selectedDrone.droneVelocity.vitesseDroneY = desiredVelocityLocal.y;
        selectedDrone.droneVelocity.vitesseDroneZ = desiredVelocityLocal.z;
    }

    //draw the vector velocity of drone
/*
    void OnDrawGizmos()
    {
        // Ensure there is a selected drone
        if (selectedDrone == null)
            return;

        // Get the current position of the drone
        Vector3 dronePosition = new Vector3(
            selectedDrone.dronePosition.positionDroneX,
            selectedDrone.dronePosition.positionDroneY,
            selectedDrone.dronePosition.positionDroneZ
        );

        // Retrieve the drone's velocity
        //switch (selectedDrone.droneVelocity.vitesseDroneX)
        Vector3 droneVelocity = new Vector3(
            selectedDrone.droneVelocity.vitesseDroneX,
            selectedDrone.droneVelocity.vitesseDroneZ,
            selectedDrone.droneVelocity.vitesseDroneY
        );

        // Draw the velocity vector as an arrow
        Gizmos.color = Color.red; // Set the color of the arrow
        Vector3 arrowHead = dronePosition + droneVelocity; // Calculate the position of the arrowhead
        Gizmos.DrawLine(dronePosition, arrowHead); // Draw the line part of the arrow

        // Draw the arrowhead
        // You may adjust the size and angle of the arrowhead as needed
        Gizmos.DrawRay(arrowHead, Quaternion.LookRotation(droneVelocity) * Quaternion.Euler(0, 135, 0) * Vector3.forward * 0.5f);
        Gizmos.DrawRay(arrowHead, Quaternion.LookRotation(droneVelocity) * Quaternion.Euler(0, 225, 0) * Vector3.forward * 0.5f);
    }*/
}
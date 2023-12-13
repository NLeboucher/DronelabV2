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

    private List<GameObject> droneObjects = new List<GameObject>(); // Liste pour stocker les GameObjects des drones

    public static bool droneConected = false;
    public static DroneInformation[] droneInformation = null; // array pour stocker les informations des drones
    public static bool isCoroutineCheckDroneConnectionRunning = false;
    public static bool isCoroutineGetFromAPIRunning = false;
    public static bool droneInitialized = false;
    public static bool isCoroutineTakeOffRunning = false;
    public static bool isCoroutineLandRunning = false;
    public static bool isCoroutineCloseLinksRunning = false;

   

    private void Update()
    {

        TakOffAndLandManagement();

        ControlAPI();

        

        if (droneConected == true && droneInformation != null && droneInformation.Length > 0 && droneInitialized == false && droneInformation[0].positionInfo)
        {
            InitialiserDrone();
        }
        // Si vous ne voulez pas utiliser l'API, vous pouvez simplement appeler la méthode UpdateDroneInfo() ici
        if (droneAPITracking)
        {
            if (droneObjects.Count > 0)
            {
                for (int i = 0; i < droneInformation.Length; i++)
                {
                    droneObjects[i].GetComponent<DroneBehavior>().UpdateDroneInfo(droneInformation[i]);
                    droneObjects[i].transform.position = new Vector3(droneInformation[i].positionDroneX, droneInformation[i].positionDroneZ, droneInformation[i].positionDroneY);
                    droneObjects[i].transform.rotation = Quaternion.Euler(0, droneInformation[i].rotationDroneYaw, 0);  
                    
                }


            }
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
        // Le cas où vous ne voulez pas utiliser l'API ou appeler InitialiserDrone() pourrait être traité ici
    }

    void InitialiserDrone()
    {
        droneInitialized = true;
        numberOfDrones = droneInformation.Length;
        for (int i = 0; i < numberOfDrones; i++)
        {
            Vector3 posDrone = new Vector3(droneInformation[i].positionDroneX, droneInformation[i].positionDroneZ, droneInformation[i].positionDroneY);
            Vector3 rotDrone = new Vector3(0, droneInformation[i].rotationDroneYaw, 0);

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
            if (droneConected && droneInformation != null && droneInformation.Length > 0 && !droneInformation[0].takeoff == false && !isCoroutineTakeOffRunning)
            {
                StartCoroutine(APIHelper.TakeOff());
            }

            else if (!droneConected )
            {
                APITakeOff = false;
            }
        }

        else if (!APITakeOff)
        {
            if (droneConected  && droneInformation != null && droneInformation.Length > 0 && droneInformation[0].takeoff  && !isCoroutineLandRunning)
            {
                StartCoroutine(APIHelper.Land());
            }
        }



    }
}

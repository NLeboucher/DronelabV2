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

   

    private void Update()
    {

        TakOffAndLandManagement();

        if (APIRequest)
        {
            ControlAPI();
        }
        else
        {
            // Si vous ne voulez pas utiliser l'API, vous pouvez simplement appeler la méthode InitialiserDrone() ici

        }
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
        if (droneConected == false && DroneControle.isCoroutineCheckDroneConnectionRunning == false)
        {
            StartCoroutine(APIHelper.CheckDroneConnection());


        }
        else if (droneConected == true && DroneControle.isCoroutineGetFromAPIRunning == false)
        {
            StartCoroutine(APIHelper.GetFromAPI());
        }



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
            if (droneConected == true && droneInformation != null && droneInformation.Length > 0 && droneInformation[0].takeoff == false)
            {
                StartCoroutine(APIHelper.TakeOff());
            }

            else
            {
                APITakeOff = false;
            }
        }

        else
        {
            if (droneConected == true && droneInformation != null && droneInformation.Length > 0 && droneInformation[0].takeoff == true)
            {
                StartCoroutine(APIHelper.Land());
            }
        }



    }
}

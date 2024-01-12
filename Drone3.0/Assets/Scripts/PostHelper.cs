using System;
using System.Collections;
using System.Collections.Generic;
using Unity.VisualScripting;
using UnityEngine;
using UnityEngine.Networking;

// this script is to test the post request 
// it is not used in the project

public class PostHelper : MonoBehaviour
{
    [SerializeField] bool post = false;
    // Start is called before the first frame update
    void Start()
    {

        // Supposons que vous testiez avec 3 drones
        DroneSwarmControle.droneInformation = new List<DroneInformation>();

        // Créez de fausses données pour chaque drone
        for (int i = 0; i < 3; i++)
        {
            DroneSwarmControle.droneInformation.Add (new DroneInformation
            {
                droneIP = "192.168.0." + (i + 1),
                takeoff = true,
                dronePosition = new DronePosition
                {
                    positionInfo = true,
                    positionDroneX = (float)Math.Round(UnityEngine.Random.Range(-5.0f, 5.0f), 2),
                    positionDroneY = (float)Math.Round(UnityEngine.Random.Range(0.0f, 10.0f), 2),
                    positionDroneZ = (float)Math.Round(UnityEngine.Random.Range(-5.0f, 5.0f), 2),
                    rotationDroneYaw = (int)UnityEngine.Random.Range(0, 360)
                },
                droneVelocity = new DroneVelocity
                {
                    vitesseDroneX = (float)Math.Round(UnityEngine.Random.Range(-1.0f, 1.0f), 2),
                    vitesseDroneY = (float)Math.Round(UnityEngine.Random.Range(-1.0f, 1.0f), 2),
                    vitesseDroneZ = (float)Math.Round(UnityEngine.Random.Range(-1.0f, 1.0f), 2),
                    vitesseDroneYaw = (float)Math.Round(UnityEngine.Random.Range(-30.0f, 30.0f), 2)
                }
            });
        }
    }
    private void Update()
    {
        if (post)
        {
            StartCoroutine(PostData());
            post = false;
        }
    }
    IEnumerator PostData()
    {

        if (DroneSwarmControle.droneInformation == null)
        {
            Debug.LogError("droneInformation is null");
            yield break; // Arrête la coroutine si droneInformation est null
        }

        DroneSpeedDataList droneSpeedDataList = new DroneSpeedDataList();

        for (int i = 0; i < DroneSwarmControle.droneInformation.Count; i++)
        {
            DroneSpeedData data = new DroneSpeedData
            {
                Vx = DroneSwarmControle.droneInformation[i].droneVelocity.vitesseDroneX,
                Vy = DroneSwarmControle.droneInformation[i].droneVelocity.vitesseDroneY,
                Vz = DroneSwarmControle.droneInformation[i].droneVelocity.vitesseDroneZ,
                yaw_rate = DroneSwarmControle.droneInformation[i].droneVelocity.vitesseDroneYaw
            };
            droneSpeedDataList.drones.Add(data);
        }

        // Serialize the drone speed data list to JSON
        string json = JsonUtility.ToJson(droneSpeedDataList);
        Debug.Log("json: " + json);

        // Create a new UnityWebRequest for sending a POST request
        UnityWebRequest www = new UnityWebRequest("https://httpbin.org/post", "POST");

        // Convert the JSON string to a byte array
        byte[] jsonToSend = new System.Text.UTF8Encoding().GetBytes(json);

        // Set up the request's upload handler with the byte array
        www.uploadHandler = (UploadHandler)new UploadHandlerRaw(jsonToSend);

        // Set up a download handler to receive the response
        www.downloadHandler = (DownloadHandler)new DownloadHandlerBuffer();

        // Set the request's content type to JSON
        www.SetRequestHeader("Content-Type", "application/json");

        // Send the web request and wait for the response
        yield return www.SendWebRequest();

        // Check if the request was successful and log the response
        if (www.result != UnityWebRequest.Result.Success)
        {
            Debug.Log(www.error);
        }
        else
        {
            Debug.Log("Response: " + www.downloadHandler.text);
        }

        // Dispose of the web request
        www.Dispose();
    }



}

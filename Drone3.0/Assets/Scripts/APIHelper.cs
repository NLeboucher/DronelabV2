using System;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using static DroneControle;
using Newtonsoft.Json;
using System.Globalization;

public class APIHelper : MonoBehaviour
{
    public static string APILocalhost = "172.21.72.102:8000";


    public static IEnumerator CheckDroneConnection()
    {
        DroneControle.isCoroutineCheckDroneConnectionRunning = true;
        Debug.Log("Début de la Coroutine CheckDroneConnection");
        string url = "http://" + APILocalhost + "/OpenLinks/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion réussie
            DroneControle.droneConected = true;
            string jsonResponse = request.downloadHandler.text;
            DroneApiResponse response = JsonUtility.FromJson<DroneApiResponse>(jsonResponse);

            // Créer et remplir le tableau de DroneInformation avec les IPs
            DroneControle.droneInformation = new DroneInformation[response.URIS.Length];
            for (int i = 0; i < response.URIS.Length; i++)
            {
                DroneControle.droneInformation[i] = new DroneInformation { droneIP = response.URIS[i] };
            }
        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine CheckDroneConnection");
        
        DroneControle.isCoroutineCheckDroneConnectionRunning = false;
    }

    public static IEnumerator TakeOff()
    {
        Debug.Log("Début de la Coroutine TakeOff");
        string url = "http://" + APILocalhost + "/takeoff/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion réussie
            for (int i = 0;i < droneInformation.Length; i++)
            {
                droneInformation[i].takeoff = true;
            }
           
        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine TakeOff");
    }
    
    public static IEnumerator Land()
    {
        Debug.Log("Début de la Coroutine Land");
        string url = "http://" + APILocalhost + "/land/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion réussie
            for (int i = 0; i < droneInformation.Length; i++)
            {
                droneInformation[i].takeoff = false;
            }

        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine Land");
    }

    public static IEnumerator GetFromAPI() 
    {
        DroneControle.isCoroutineGetFromAPIRunning = true;
        Debug.Log("Début de la Coroutine GetFromAPI");
        string url = "http://" + APILocalhost + "/getposition/";

        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse
        Debug.Log("request.resultGetFromAPI = " + request.result);

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
            DroneControle.droneConected = false;
        }
        else
        {
            // Successfully received response
            string jsonResponse = request.downloadHandler.text;
            Debug.Log("Contenu de la réponse JSON: " + jsonResponse);

            //DronePositionResponse dronePosision = JsonUtility.FromJson<DronePositionResponse>(jsonResponse);
            DronePositionResponse dronePosition = Newtonsoft.Json.JsonConvert.DeserializeObject<DronePositionResponse>(jsonResponse);

            Debug.Log("information stocked in DronePositionResponse = "+ dronePosition.position["IP1"]["X"]);

            // arrange values of dronePosision in droneInformation
            if (droneInformation != null)                                               
            {
                for (int i = 0; i < droneInformation.Length; i++)
                {
                    if (dronePosition.position.ContainsKey(droneInformation[i].droneIP))
                    {
                        float x, y, z, yaw;
                        //L'utilisation de CultureInfo.InvariantCulture garantit que le point est toujours utilisé comme séparateur décimal, même si la culture actuelle définit une virgule comme séparateur décimal.
                        if (float.TryParse(dronePosition.position[droneInformation[i].droneIP]["X"], NumberStyles.Any, CultureInfo.InvariantCulture, out  x) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["Y"], NumberStyles.Any, CultureInfo.InvariantCulture, out  y) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["Z"], NumberStyles.Any, CultureInfo.InvariantCulture, out  z) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["yaw"], NumberStyles.Any, CultureInfo.InvariantCulture, out  yaw))
                        {
                            droneInformation[i].positionDroneX = x;
                            droneInformation[i].positionDroneY = y;
                            droneInformation[i].positionDroneZ = z;
                            droneInformation[i].rotationDroneYaw = yaw;
                            Debug.Log("droneInformation[" + i + "] = " + droneInformation[i].droneIP + " " + droneInformation[i].positionDroneX + " " + droneInformation[i].positionDroneY + " " + droneInformation[i].positionDroneZ + " " + droneInformation[i].rotationDroneYaw);
                        }
                        else
                        {
                            Debug.LogError("Erreur lors de la conversion des valeurs en float.");
                        }

                    }
                }
            }
            else
            {
                Debug.LogError("droneInformation is null");
            }   
            

        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine GetFromAPI");
        DroneControle.isCoroutineGetFromAPIRunning = false;
    }





}


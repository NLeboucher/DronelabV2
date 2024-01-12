using System;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;
using static DroneSwarmControle;
using Newtonsoft.Json;
using System.Globalization;

public class APIHelper : MonoBehaviour
{
    
    //public static string APILocalhost = "172.21.73.34:8080";
    //public static string APILocalhost = "192.168.1.29:8000";
    public static string APILocalhost = "172.21.72.165:8000";

    #region API Get Classes
    public static IEnumerator CheckDroneConnection()
    {
        DroneSwarmControle.isCoroutineCheckDroneConnectionRunning = true;
        Debug.Log("Début de la Coroutine CheckDroneConnection");
        string url = "http://" + APILocalhost + "/OpenLinks/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            DroneSwarmControle.isCoroutineCheckDroneConnectionRunning = false;
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion réussie
            
            string jsonResponse = request.downloadHandler.text;
            DroneApiResponse response = JsonUtility.FromJson<DroneApiResponse>(jsonResponse);
            Debug.Log("Contenu de la réponse OpenLinks JSON: " + jsonResponse);
            // Créer et remplir le tableau de DroneInformation avec les IPs
            DroneSwarmControle.droneInformation = new List<DroneInformation>(response.URIS.Length);
            Debug.Log("Nombre de drones connectés: " + response.URIS.Length);
            if (response.URIS.Length == 0)
            {
                Debug.LogError("Aucun drone n'est connecté");
            }
            else
            {
                DroneSwarmControle.droneConected = true;
            }
            for (int i = 0; i < response.URIS.Length; i++)
            {
                DroneSwarmControle.droneInformation.Add(new DroneInformation
                {
                    droneIP = response.URIS[i],
                    dronePosition = new DronePosition(), // Initialize DronePosition
                    droneVelocity = new DroneVelocity()  // Initialize DroneVelocity
                });
                Debug.Log("droneInformation[" + i + "] = " + DroneSwarmControle.droneInformation[i].droneIP);
            }

        }
        yield return new WaitForSeconds(1);
        DroneSwarmControle.isCoroutineCheckDroneConnectionRunning = false;
        Debug.Log("Fin de la Coroutine CheckDroneConnection");
        
        
    }

    public static IEnumerator TakeOff()
    {
        Debug.Log("Début de la Coroutine TakeOff");
        DroneSwarmControle.isCoroutineTakeOffRunning = true;
        string url = "http://" + APILocalhost + "/All_TakeOff/";
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
            for (int i = 0;i < droneInformation.Count; i++)
            {
                droneInformation[i].takeoff = true;
            }
           
        }
        yield return new WaitForSeconds(0.2f);
        DroneSwarmControle.isCoroutineTakeOffRunning = false;
        Debug.Log("Fin de la Coroutine TakeOff");
    }
    
    public static IEnumerator Land()
    {
        Debug.Log("Début de la Coroutine Land");
        DroneSwarmControle.isCoroutineLandRunning = true;
        string url = "http://" + APILocalhost + "/All_Land/";
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
            for (int i = 0; i < droneInformation.Count; i++)
            {
                droneInformation[i].takeoff = false;
            }

        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine Land");
        DroneSwarmControle.isCoroutineLandRunning = false;
    }

    public static IEnumerator GetFromAPI() 
    {
        DroneSwarmControle.isCoroutineGetFromAPIRunning = true;
        Debug.Log("Début de la Coroutine GetFromAPI");
        string url = "http://" + APILocalhost + "/getestimatedpositions/";

        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse
        Debug.Log("request.resultGetFromAPI = " + request.result);

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
            
        }
        else
        {
            // Successfully received response
            string jsonResponse = request.downloadHandler.text;
            //Debug.Log("Contenu de la réponse  de getposition JSON: " + jsonResponse);

            
            DronePositionResponse dronePosition = Newtonsoft.Json.JsonConvert.DeserializeObject<DronePositionResponse>(jsonResponse);

            

            // arrange values of dronePosision in droneInformation
            if (droneInformation != null)                                               
            {
                for (int i = 0; i < droneInformation.Count; i++)
                {
                    //Debug.Log( "Type de position "+dronePosition.Positions[droneInformation[i].droneIP][0].GetType());
                    if (dronePosition.Positions.ContainsKey(droneInformation[i].droneIP))
                    {
                        DroneSwarmControle.droneInformation[i].dronePosition.positionInfo = true;
                        DroneSwarmControle.droneInformation[i].dronePosition.positionDroneX = dronePosition.Positions[droneInformation[i].droneIP][0];
                        DroneSwarmControle.droneInformation[i].dronePosition.positionDroneY = dronePosition.Positions[droneInformation[i].droneIP][1];
                        DroneSwarmControle.droneInformation[i].dronePosition.positionDroneZ = dronePosition.Positions[droneInformation[i].droneIP][2]; 
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
        DroneSwarmControle.isCoroutineGetFromAPIRunning = false;
    }

    public static IEnumerator CloseLinks()
    {
        Debug.Log("Début de la Coroutine CloseLinks");
        DroneSwarmControle.isCoroutineCloseLinksRunning = true;
        string url = "http://" + APILocalhost + "/CloseLinks/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion pour CloseLinks: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion réussie
            Debug.Log("Links fermés");
            DroneSwarmControle.droneConected = false;
        }
        yield return new WaitForSeconds(0.2f);
        DroneSwarmControle.isCoroutineCloseLinksRunning = false;
        Debug.Log("Fin de la Coroutine CloseLinks");
    }

    #endregion


    #region API Set Classes



    public static IEnumerator SetVelocityToAPI()
    {
        DroneSwarmControle.isCoroutineSetVelocity = true;
        Debug.Log("Début de la Coroutine SetVelocityToAPI");

        string url = "http://" + APILocalhost + "/all_startlinearmotion";

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
        UnityWebRequest www = new UnityWebRequest(url, "POST");

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
        yield return new WaitForSeconds(0.2f);
        DroneSwarmControle.isCoroutineSetVelocity = false;
        Debug.Log("Fin de la Coroutine SetVelocityToAPI");
    
    }



    

    public static IEnumerator SetGoToAPI (DroneInformation[] droneInformation, int GoToX, int GoToY, int GoToZ, int droneSpeed)
    {
        if (droneInformation != null)
        {
            string url = "http://" + APILocalhost + "/goto";
            for (int i = 0; i < droneInformation.Length; i++)
            {
                url = url + "/" + droneInformation[i].droneIP + "," + GoToX.ToString() + "," + GoToY.ToString() + "," + GoToZ.ToString() + "," + droneSpeed.ToString() +";";
            }
            if (url.Length > 0)
            {
                string modifiedurl = url.Substring(0, url.Length - 1);
                // Utilisez modifiedString qui a le dernier caractère enlevé (le point-virgule)
                url = modifiedurl + "/";
            }
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
                Debug.Log("GoTo du drone " + droneInformation[0].droneIP + " mis à jour");
            }

        }

        else
        {
            Debug.LogError("droneInformation is null");
        }
        yield return new WaitForSeconds(0.2f);
    }



    #endregion



}


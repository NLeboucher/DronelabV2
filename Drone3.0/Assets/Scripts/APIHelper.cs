using System;
using System.IO;
using System.Net;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using System.Collections.Generic;


public class APIHelper : MonoBehaviour
{


    public static IEnumerator CheckDroneConnection()
    {
        string url = "http://ip/OpenLinks/";
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requête et attend la réponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            string jsonResponse = request.downloadHandler.text;
            DroneApiResponse response = JsonUtility.FromJson<DroneApiResponse>(jsonResponse);

            // Créer et remplir le tableau de DroneInformation avec les IPs
            DroneControle.droneInformation = new DroneInformation[response.URIS.Length];
            for (int i = 0; i < response.URIS.Length; i++)
            {
                DroneControle.droneInformation[i] = new DroneInformation { droneIP = response.URIS[i] };
            }
        }
    }

    public static IEnumerator GetFromAPI() 
    {
        string uri = "http://172.21.73.34:8000/getposition/";
        UnityWebRequest request = UnityWebRequest.Get(uri);

        // Send the request and wait for a response
        yield return request.SendWebRequest();

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
        }
        else
        {
            // Successfully received response
            string json = request.downloadHandler.text;
            DroneInformation droneInfo = JsonUtility.FromJson<DroneInformation>(json);
            // Do something with the droneInfo
            Debug.Log(droneInfo.droneIP);
        }
    }

}


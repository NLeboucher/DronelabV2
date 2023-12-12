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
    public static string APILocalhost = "172.21.72.102:8000";

    #region API Get Classes
    public static IEnumerator CheckDroneConnection()
    {
        DroneSwarmControle.isCoroutineCheckDroneConnectionRunning = true;
        Debug.Log("D�but de la Coroutine CheckDroneConnection");
        string url = "http://" + APILocalhost + "/OpenLinks/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion r�ussie
            DroneSwarmControle.droneConected = true;
            string jsonResponse = request.downloadHandler.text;
            DroneApiResponse response = JsonUtility.FromJson<DroneApiResponse>(jsonResponse);

            // Cr�er et remplir le tableau de DroneInformation avec les IPs
            DroneSwarmControle.droneInformation = new DroneInformation[response.URIS.Length];
            for (int i = 0; i < response.URIS.Length; i++)
            {
                DroneSwarmControle.droneInformation[i] = new DroneInformation { droneIP = response.URIS[i] };
            }
        }
        yield return new WaitForSeconds(0.2f);
        Debug.Log("Fin de la Coroutine CheckDroneConnection");
        
        DroneSwarmControle.isCoroutineCheckDroneConnectionRunning = false;
    }

    public static IEnumerator TakeOff()
    {
        Debug.Log("D�but de la Coroutine TakeOff");
        string url = "http://" + APILocalhost + "/takeoff/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion r�ussie
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
        Debug.Log("D�but de la Coroutine Land");
        string url = "http://" + APILocalhost + "/land/";
        Debug.Log(url);
        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Erreur de connexion: " + request.error);
            // Gestion des erreurs, droneConected reste false
        }
        else
        {
            // Connexion r�ussie
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
        DroneSwarmControle.isCoroutineGetFromAPIRunning = true;
        Debug.Log("D�but de la Coroutine GetFromAPI");
        string url = "http://" + APILocalhost + "/getposition/";

        UnityWebRequest request = UnityWebRequest.Get(url);
        yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse
        Debug.Log("request.resultGetFromAPI = " + request.result);

        if (request.result != UnityWebRequest.Result.Success)
        {
            Debug.LogError("Error: " + request.error);
            DroneSwarmControle.droneConected = false;
        }
        else
        {
            // Successfully received response
            string jsonResponse = request.downloadHandler.text;
            Debug.Log("Contenu de la r�ponse JSON: " + jsonResponse);

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
                        //L'utilisation de CultureInfo.InvariantCulture garantit que le point est toujours utilis� comme s�parateur d�cimal, m�me si la culture actuelle d�finit une virgule comme s�parateur d�cimal.
                        if (float.TryParse(dronePosition.position[droneInformation[i].droneIP]["X"], NumberStyles.Any, CultureInfo.InvariantCulture, out  x) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["Y"], NumberStyles.Any, CultureInfo.InvariantCulture, out  y) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["Z"], NumberStyles.Any, CultureInfo.InvariantCulture, out  z) &&
                            float.TryParse(dronePosition.position[droneInformation[i].droneIP]["yaw"], NumberStyles.Any, CultureInfo.InvariantCulture, out  yaw))
                        {
                            droneInformation[i].positionInfo = true;
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
        DroneSwarmControle.isCoroutineGetFromAPIRunning = false;
    }

    #endregion


    #region API Set Classes

    public static IEnumerator SetVelocityToAPI(DroneInformation[] droneInformation)
    {
        if (droneInformation != null)
        {
            string url = "http://" + APILocalhost + "/setvelocity";
            for (int i = 0; i < droneInformation.Length; i++)
            {
                url = url + "/" + droneInformation[i].droneIP + "," + droneInformation[i].vitesseDroneX + "," + droneInformation[i].vitesseDroneY + "," + droneInformation[i].vitesseDroneZ + "," + droneInformation[i].vitesseDroneYaw + ";";
            }
            if (url.Length > 0)
            {
                string modifiedurl = url.Substring(0, url.Length - 1);
                // Utilisez modifiedString qui a le dernier caract�re enlev� (le point-virgule)
                url = modifiedurl + "/";
            }
            Debug.Log(url);
            UnityWebRequest request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse
            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Erreur de connexion: " + request.error);
                // Gestion des erreurs, droneConected reste false
            }
            else
            {
                // Connexion r�ussie
                Debug.Log("Vitesse du drone " + droneInformation[0].droneIP + " mise � jour");
            }

        }
        
        else
        {
            Debug.LogError("droneInformation is null");
        }
        yield return new WaitForSeconds(0.2f);
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
                // Utilisez modifiedString qui a le dernier caract�re enlev� (le point-virgule)
                url = modifiedurl + "/";
            }
            Debug.Log(url);
            UnityWebRequest request = UnityWebRequest.Get(url);
            yield return request.SendWebRequest();  // Envoie la requ�te et attend la r�ponse
            if (request.result != UnityWebRequest.Result.Success)
            {
                Debug.LogError("Erreur de connexion: " + request.error);
                // Gestion des erreurs, droneConected reste false
            }
            else
            {
                // Connexion r�ussie
                Debug.Log("GoTo du drone " + droneInformation[0].droneIP + " mis � jour");
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


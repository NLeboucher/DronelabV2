using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneBehavior : MonoBehaviour
{
    public DroneInformation droneInfo;

    public void Initialiser(DroneInformation info)
    {
        droneInfo = info;
        // Initialisation supplémentaire si nécessaire
    }

    public void UpdateDroneInfo(DroneInformation newInfo)
    {
        droneInfo = newInfo;
        // Effectuez ici toute mise à jour nécessaire en fonction des nouvelles informations
    }
    public void Update()
    {
        // Effectuez ici toute mise à jour nécessaire en fonction des informations du drone
    }
}

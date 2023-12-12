using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class DroneBehavior : MonoBehaviour
{
    public DroneInformation droneInfo;

    public void Initialiser(DroneInformation info)
    {
        droneInfo = info;
        // Initialisation suppl�mentaire si n�cessaire
    }

    public void UpdateDroneInfo(DroneInformation newInfo)
    {
        droneInfo = newInfo;
        // Effectuez ici toute mise � jour n�cessaire en fonction des nouvelles informations
    }
    public void Update()
    {
        // Effectuez ici toute mise � jour n�cessaire en fonction des informations du drone
    }
}

using System.Collections.Generic;

[System.Serializable]

public class DroneApiResponse//utilliser les trucs de noé pour les stocker dans des game object ou jsp quoi
{
    public string[] URIS;
}

[System.Serializable]
public class DronePositionResponse
{
    public Dictionary<string, Dictionary<string, string>> position;
}

public class DroneInformation  //maybe attache to game object
{
    public string droneIP;
    public bool takeoff = false;
    public bool positionInfo = false;
    public float positionDroneX;
    public float positionDroneY;
    public float positionDroneZ;
    public float rotationDroneYaw;
    public float vitesseDroneX;
    public float vitesseDroneY;
    public float vitesseDroneZ;
    public float vitesseDroneYaw;

}



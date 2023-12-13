using System.Collections.Generic;

[System.Serializable]

public class DroneApiResponse//utilliser les trucs de noé pour les stocker dans des game object ou jsp quoi
{
    public string[] URIS;
}

[System.Serializable]
public class DronePositionResponse
{
    public Dictionary<string, float[]> Positions;
}

public class DroneInformation  //maybe attache to game object
{
    public string droneIP;
    public bool takeoff = false;
    public bool positionInfo = false;
    public float positionDroneX;
    public float positionDroneY;
    public float positionDroneZ;
    public float rotationDroneYaw = 0;
    public float vitesseDroneX;
    public float vitesseDroneY;
    public float vitesseDroneZ;
    public float vitesseDroneYaw;

}



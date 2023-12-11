using System.Collections.Generic;

[System.Serializable]

public class DroneApiResponse
{
    public string[] URIS;
}

[System.Serializable]
public class DronePositionResponse
{
    public Dictionary<string, Dictionary<string, string>> position;
}

public class DroneInformation 
{
    public string droneIP;
    public bool takeoff;
    
    public float positionDroneX;
    public float positionDroneY;
    public float positionDroneZ;
    public float rotationDroneYaw;

}



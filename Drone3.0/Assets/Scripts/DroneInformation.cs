[System.Serializable]

public class DroneApiResponse
{
    public string[] URIS;
}
public class DroneInformation 
{
    public string droneIP;
    public bool droneTakeoff;
    public float positionDroneX;
    public float positionDroneY;
    public float positionDroneZ;
    public float rotationDroneYaw;

}


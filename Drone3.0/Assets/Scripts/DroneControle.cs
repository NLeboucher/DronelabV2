using JetBrains.Annotations;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using System.Collections.Concurrent;




public class DroneControle : MonoBehaviour
{
    #region variables region

    [SerializeField] private float distThreshold = 1f;
    [SerializeField] private float droneSpeed = 5f;
    //[SerializeField] private float Drone_Rotation_Speed = 5f; //pour le tilt mais ça marche pas 
    //[SerializeField] private float Drone_Tilt_Angle = 30f;
    [SerializeField] private float Drone_Turn_Speed = 50f;
    [SerializeField] private int Go_To_X = 0;
    [SerializeField] private int Go_To_Y = 0;
    [SerializeField] private int Go_To_Z = 0;
    [SerializeField] private bool Bool_Go_To = false;
    [SerializeField] private bool APIRequest = false;
    [SerializeField] private bool APITakeOff = false;
    

    Vector3 Input_Vector_Position = new Vector3(0, 0, 0);
    float Input_Vector_Rotation = 0f; // Rotation horizontale
    public static bool droneConected = false;
    public static DroneInformation[] droneInformation = null;
    public static bool isCoroutineCheckDroneConnectionRunning = false;
    public static bool isCoroutineGetFromAPIRunning = false;

    #endregion



    private void Update()
    {

        


        Input_Vector_Rotation = 0f;
        Input_Vector_Position = Vector3.zero;

        #region inputs region
        if (Input.GetKey(KeyCode.W))
        {
            Input_Vector_Position.y = +1;

        }
        if (Input.GetKey(KeyCode.A))
        {
            Input_Vector_Position.x = -1;

        }
        if (Input.GetKey(KeyCode.D))
        {
            Input_Vector_Position.x = +1;

        }
        if (Input.GetKey(KeyCode.S))
        {
            Input_Vector_Position.y = -1;

        }

        if (Input.GetKey(KeyCode.Space))
        {
            Input_Vector_Position.z = +1;
        }
        if (Input.GetKey(KeyCode.LeftShift))
        {
            Input_Vector_Position.z = -1;
        }

        if (Input.GetKey(KeyCode.Q))
        {
            //Input_Vector_Rotation = -Drone_Turn_Speed;
            Input_Vector_Rotation = -1;
        }
        if (Input.GetKey(KeyCode.E))
        {
            //Input_Vector_Rotation = Drone_Turn_Speed;
            Input_Vector_Rotation = 1;
        }
        if (Input.GetKeyDown(KeyCode.F))
        {
            if (Bool_Go_To)
            {
                Bool_Go_To = false;
            }
            else
            {
                Bool_Go_To = true;
            }
        }
        if (Input.GetKeyDown(KeyCode.X))
        {
            if (APIRequest)
            {
                APIRequest = false;
            }
            else
            {
                APIRequest = true;
            }
        }

        if (Input.GetKeyDown(KeyCode.T))
        {
            if (APITakeOff)
            {
                APITakeOff = false;
            }
            else
            {
                APITakeOff = true;
            }
        }
        #endregion

        if (Bool_Go_To)
        {
            CalculateInputsForTarget_Position();
        }
        
        if (APITakeOff)
        {
            if (droneConected == true && droneInformation!= null && droneInformation.Length > 0 && droneInformation[0].takeoff==false)
            {
                StartCoroutine(APIHelper.TakeOff());
            }
            
            else
            {
                APITakeOff = false;
            }
        }

        else
        {
            if (droneConected == true && droneInformation != null && droneInformation.Length > 0 && droneInformation[0].takeoff == true)
            {
                StartCoroutine(APIHelper.Land());
            }
        }

        if (APIRequest)
        {
            ControlAPI();
        }
        



        /*// Calcul du tilt en fonction de Input_Vector_Position
        Vector3 Drone_tilt_when_mooving_vector = new Vector3(
            Input_Vector_Position.y * Drone_Tilt_Angle, // Tilt avant/arrière
            0,
            -Input_Vector_Position.x * Drone_Tilt_Angle // Tilt gauche/droite
        );*/

        Vector3 Input_Vector_Position_Normalized_XY = new Vector3(Input_Vector_Position.x, Input_Vector_Position.y, 0).normalized;

        // Créer le vecteur de mouvement en incluant la composante z séparément
        Vector3 moveDir = new Vector3(Input_Vector_Position_Normalized_XY.x, Input_Vector_Position.z, Input_Vector_Position_Normalized_XY.y);

        transform.Translate(moveDir * droneSpeed * Time.deltaTime, Space.Self);

        // Rotation locale autour de l'axe Y
        if (Input_Vector_Rotation != 0)
        {

            float rotationAmount = Input_Vector_Rotation * Drone_Turn_Speed * Time.deltaTime;
            // Appliquer la rotation autour de l'axe Y local
            transform.Rotate(Vector3.up, rotationAmount);
        }


        Debug.Log(droneInformation[0].droneIP);
        Debug.Log(droneInformation[0].positionDroneX);
    }




    void CalculateInputsForTarget_Position()
    {

        Vector3 targetPos = new Vector3(Go_To_X, Go_To_Y, Go_To_Z);



        Vector3 forward = transform.forward;
        forward.y = 0; // Ignorer la hauteur pour la direction

        Vector3 targetPositionOnSamePlane = new Vector3(Go_To_X, transform.position.y, Go_To_Z);
        Vector3 targetDirection = (targetPositionOnSamePlane - transform.position).normalized;
        targetDirection.y = 0; // Encore une fois, ignorer la hauteur

        // Calculer l'angle entre la direction actuelle du drone et la direction vers la cible
        float angleToTarget = Vector3.SignedAngle(forward, targetDirection, Vector3.up);




        if (Mathf.Abs(angleToTarget) > 1f) // Seuil pour commencer à tourner
        {
            
            // Déterminer si l'angle nécessite une rotation à gauche (-1) ou à droite (+1)
            Input_Vector_Rotation = angleToTarget > 0 ? 1 : -1;
            Input_Vector_Position = Vector3.zero;
        }
        else
        {
            

            // calculer et appliquer l'input de position une fois orienté vers la cible avec les axes de unity
            Vector3 vecDistWorld = (targetPos - transform.position);
            // Convertir ce vecteur dans l'espace local du drone
            Vector3 vecDistLocal = transform.InverseTransformDirection(vecDistWorld);
            //on inverse pour avoir le xyz pour les humain normal
            Vector3 inputposition = new Vector3(vecDistLocal.x, vecDistLocal.z, vecDistLocal.y);
            Input_Vector_Position = inputposition;

            


            if (vecDistLocal.magnitude < distThreshold)
            {
                Bool_Go_To = false;
            }


        }
    }

    void ControlAPI()
    {
        if (droneConected == false && DroneControle.isCoroutineCheckDroneConnectionRunning == false)
        {
            StartCoroutine(APIHelper.CheckDroneConnection());


        }
        else if (droneConected == true && DroneControle.isCoroutineGetFromAPIRunning == false)
        {
            StartCoroutine(APIHelper.GetFromAPI());
        }



    }





}
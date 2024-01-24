using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(DroneSwarmControle))]
public class DroneSwarmControleEditor : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        base.OnInspectorGUI();

        if (DroneSwarmControle.droneInformation != null && DroneSwarmControle.droneInformation.Count > 0)
        {
            // Create dropdown options for drones
            string[] options = new string[DroneSwarmControle.droneInformation.Count];
            for (int i = 0; i < options.Length; i++)
            {
                options[i] = "Drone " + (i + 1); // Or use any unique identifier like IP
            }

            // Dropdown to select a drone
            int currentIndex = DroneSwarmControle.selectedDroneIndex < 0 ? 0 : DroneSwarmControle.selectedDroneIndex;
            DroneSwarmControle.selectedDroneIndex = EditorGUILayout.Popup("Select Drone", currentIndex, options);

            // Display positions for each drone
            EditorGUILayout.Space();
            EditorGUILayout.LabelField("Drone Positions", EditorStyles.boldLabel);
            for (int i = 0; i < DroneSwarmControle.droneInformation.Count; i++)
            {
                DroneInformation drone = DroneSwarmControle.droneInformation[i];
                if (drone != null && drone.dronePosition != null)
                {
                    Vector3 position = new Vector3(
                        drone.dronePosition.positionDroneX,
                        drone.dronePosition.positionDroneY,
                        drone.dronePosition.positionDroneZ
                    );

                    EditorGUILayout.Vector3Field($"Drone {i + 1} ({drone.droneIP}) Position", position);
                }
            }
        }
        else
        {
            EditorGUILayout.LabelField("No Drone Connected");
        }


    }
}

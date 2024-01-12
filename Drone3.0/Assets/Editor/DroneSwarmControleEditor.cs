using UnityEditor;
using UnityEngine;

[CustomEditor(typeof(DroneSwarmControle))]
public class DroneSwarmControleEditor : Editor
{
    public override void OnInspectorGUI()
    {
        // Draw the default inspector
        base.OnInspectorGUI();

        // Since droneInformation is a static member, access it using the class name
        string[] options;
        if (DroneSwarmControle.droneInformation != null && DroneSwarmControle.droneInformation.Count > 0)
        {
            options = new string[DroneSwarmControle.droneInformation.Count];
            for (int i = 0; i < options.Length; i++)
            {
                options[i] = "Drone " + (i + 1); // Or use any unique identifier
            }
        }
        else
        {
            options = new string[] { "No Drone Connected" };
            // You will also need a static field or a different approach to keep track of the selected drone index
        }

        // Handling for selected drone index (ensure this is also appropriately defined in your DroneSwarmControle class)
        int currentIndex = DroneSwarmControle.selectedDroneIndex < 0 ? 0 : DroneSwarmControle.selectedDroneIndex;
        DroneSwarmControle.selectedDroneIndex = EditorGUILayout.Popup("Select Drone", currentIndex, options);

        // Add additional GUI elements as needed
    }
}

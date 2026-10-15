using HarmonyLib;
using UnityEngine;

namespace QuantumBlink
{
    [HarmonyPatch]
    public class QuantumPatches
    {
        // Quantum objects won't appear closer than this to the ship's center (in meters).
        private const float ShipSpace = 12f;

        // Is this object (or socket) where the player or their ship is?
        private static bool IsInPersonalSpace(VisibilityObject obj)
        {
            var camera = Locator.GetPlayerCamera();
            var player = Locator.GetPlayerTransform();
            if (camera == null || player == null) return false;

            if (obj.CheckPointInside(camera.transform.position)
                || Vector3.Distance(obj.transform.position, player.position) < QuantumBlink.PersonalSpace)
                return true;

            var ship = Locator.GetShipTransform();
            return ship != null
                && Vector3.Distance(obj.transform.position, ship.position) < ShipSpace;
        }

        // 1. During a blink, the player sees nothing except their own space.
        [HarmonyPostfix]
        [HarmonyPatch(typeof(VisibilityObject), nameof(VisibilityObject.CheckVisibility))]
        public static void CheckVisibility_Postfix(VisibilityObject __instance, ref bool __result)
        {
            if (QuantumBlink.IsBlinking && !IsInPersonalSpace(__instance))
                __result = false;
        }

        // 2. During a blink, a new spot only counts as seen if the player is standing there.
        [HarmonyPostfix]
        [HarmonyPatch(typeof(VisibilityObject), nameof(VisibilityObject.CheckVisibilityInstantly))]
        public static void CheckVisibilityInstantly_Postfix(VisibilityObject __instance, ref bool __result)
        {
            if (QuantumBlink.IsBlinking)
                __result = IsInPersonalSpace(__instance);
        }

        // 3. A failed move puts the object back with a random spin. Undo the spin.
        [HarmonyPrefix]
        [HarmonyPatch(typeof(SocketedQuantumObject), nameof(SocketedQuantumObject.ChangeQuantumState))]
        public static void ChangeQuantumState_Prefix(SocketedQuantumObject __instance, out Quaternion __state)
        {
            __state = __instance.transform.rotation;
        }

        [HarmonyPostfix]
        [HarmonyPatch(typeof(SocketedQuantumObject), nameof(SocketedQuantumObject.ChangeQuantumState))]
        public static void ChangeQuantumState_Postfix(SocketedQuantumObject __instance, bool __result, Quaternion __state)
        {
            if (!__result)
                __instance.transform.rotation = __state;
        }

        // 4. Skip the game's half-second wait between moves during blinks.
        [HarmonyPrefix]
        [HarmonyPatch(typeof(QuantumObject), nameof(QuantumObject.Collapse))]
        public static void Collapse_Prefix(QuantumObject __instance)
        {
            if (QuantumBlink.IsBlinking)
                __instance._lastCollapseTime = -1f;
        }

        // Debug: log whenever a quantum object moves during a blink.
        [HarmonyPostfix]
        [HarmonyPatch(typeof(QuantumObject), nameof(QuantumObject.Collapse))]
        public static void Collapse_Postfix(QuantumObject __instance, bool __result)
        {
            if (QuantumBlink.DebugLogging && __result && QuantumBlink.IsBlinking)
                QuantumBlink.Instance.ModHelper.Console.WriteLine($"Quantum object moved during blink: {__instance.name}");
        }
    }
}
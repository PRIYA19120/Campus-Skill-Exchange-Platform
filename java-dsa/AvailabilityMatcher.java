import java.util.HashSet;
import java.util.Set;

public class AvailabilityMatcher {

    public static Set<String> findCommonAvailability(
            Set<String> studentA,
            Set<String> studentB) {

        Set<String> commonTimes = new HashSet<>(studentA);
        commonTimes.retainAll(studentB);

        return commonTimes;
    }

    public static boolean hasCommonTime(
            Set<String> studentA,
            Set<String> studentB) {

        return !findCommonAvailability(studentA, studentB).isEmpty();
    }
}
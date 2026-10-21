import java.util.HashSet;
import java.util.Set;

public class SkillMatcher {

    public static Set<String> getMatchingSkills(
            Set<String> teachSkills,
            Set<String> learnSkills) {

        Set<String> matches = new HashSet<>(teachSkills);
        matches.retainAll(learnSkills);

        return matches;
    }

    public static boolean areMutualMatches(
            Student studentA,
            Student studentB) {

        Set<String> aCanTeachB = getMatchingSkills(
                studentA.getTeachSkills(),
                studentB.getLearnSkills()
        );

        Set<String> bCanTeachA = getMatchingSkills(
                studentB.getTeachSkills(),
                studentA.getLearnSkills()
        );

        return !aCanTeachB.isEmpty()
                && !bCanTeachA.isEmpty();
    }
}
import java.util.HashSet;
import java.util.PriorityQueue;
import java.util.Set;

public class Main {

    public static int calculateSkillScore(
            Student target, Student candidate) {

        Set<String> candidateCanTeach = SkillMatcher.getMatchingSkills(
                candidate.getTeachSkills(),
                target.getLearnSkills()
        );

        Set<String> targetCanTeach = SkillMatcher.getMatchingSkills(
                target.getTeachSkills(),
                candidate.getLearnSkills()
        );

        int totalMatches = candidateCanTeach.size()
                + targetCanTeach.size();

        return Math.min(totalMatches * 50, 100);
    }

    public static void main(String[] args) {

        Student rahul = new Student(
                1,
                "Rahul",
                Set.of("Java", "Python"),
                Set.of("Web Development", "SQL")
        );

        Student priya = new Student(
                2,
                "Priya",
                Set.of("Web Development", "SQL"),
                Set.of("Java", "Python")
        );

        Student aman = new Student(
                3,
                "Aman",
                Set.of("Java", "HTML"),
                Set.of("Python", "SQL")
        );

        Student neha = new Student(
                4,
                "Neha",
                Set.of("Python", "SQL"),
                Set.of("Java", "Web Development")
        );

        // 1. Find common skills between Rahul and Priya
        System.out.println("=== Skill Matching ===");

        Set<String> matchingSkills =
                SkillMatcher.getMatchingSkills(
                        rahul.getTeachSkills(),
                        priya.getLearnSkills()
                );

        System.out.println(
                "Rahul can teach Priya: " + matchingSkills
        );

        // 2. Check whether the match is mutual
        boolean mutualMatch =
                SkillMatcher.areMutualMatches(rahul, priya);

        System.out.println("Mutual Match: " + mutualMatch);

        // 3. Check common availability
        System.out.println("\n=== Availability Matching ===");

        Set<String> rahulTimes = new HashSet<>();
        rahulTimes.add("Monday Evening");
        rahulTimes.add("Wednesday Afternoon");

        Set<String> priyaTimes = new HashSet<>();
        priyaTimes.add("Monday Evening");
        priyaTimes.add("Friday Afternoon");

        Set<String> commonTimes =
                AvailabilityMatcher.findCommonAvailability(
                        rahulTimes, priyaTimes
                );

        System.out.println("Common times: " + commonTimes);

        // 4. Rank candidates using PriorityQueue
        System.out.println("\n=== Match Ranking ===");

        Set<String> amanTimes = new HashSet<>();
        amanTimes.add("Monday Evening");

        Set<String> nehaTimes = new HashSet<>();
        nehaTimes.add("Tuesday Afternoon");

        int priyaScore = calculateSkillScore(rahul, priya);
        int amanScore = calculateSkillScore(rahul, aman);
        int nehaScore = calculateSkillScore(rahul, neha);

        boolean priyaTimeMatch =
                AvailabilityMatcher.hasCommonTime(
                        rahulTimes, priyaTimes
                );

        boolean amanTimeMatch =
                AvailabilityMatcher.hasCommonTime(
                        rahulTimes, amanTimes
                );

        boolean nehaTimeMatch =
                AvailabilityMatcher.hasCommonTime(
                        rahulTimes, nehaTimes
                );

        PriorityQueue<MatchResult> ranking =
                new PriorityQueue<>();

        ranking.offer(
                new MatchResult(priya, priyaScore, priyaTimeMatch)
        );

        ranking.offer(
                new MatchResult(aman, amanScore, amanTimeMatch)
        );

        ranking.offer(
                new MatchResult(neha, nehaScore, nehaTimeMatch)
        );

        while (!ranking.isEmpty()) {
            System.out.println(ranking.poll());
        }
    }
}
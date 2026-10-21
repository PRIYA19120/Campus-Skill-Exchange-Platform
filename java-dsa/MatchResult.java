public class MatchResult implements Comparable<MatchResult> {

    private final Student student;
    private final int skillScore;
    private final boolean timeMatch;
    private final int totalScore;

    public MatchResult(Student student, int skillScore,
                       boolean timeMatch) {
        this.student = student;
        this.skillScore = skillScore;
        this.timeMatch = timeMatch;
        this.totalScore = skillScore + (timeMatch ? 20 : 0);
    }

    public Student getStudent() {
        return student;
    }

    public int getSkillScore() {
        return skillScore;
    }

    public boolean isTimeMatch() {
        return timeMatch;
    }

    public int getTotalScore() {
        return totalScore;
    }

    @Override
    public int compareTo(MatchResult other) {
        return Integer.compare(other.totalScore, this.totalScore);
    }

    @Override
    public String toString() {
        return "Student: " + student.getName()
                + " | Skill Score: " + skillScore
                + " | Time Match: " + timeMatch
                + " | Total Score: " + totalScore;
    }
}
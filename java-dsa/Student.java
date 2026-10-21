import java.util.HashSet;
import java.util.Set;

public class Student {
    private final int id;
    private final String name;
    private final Set<String> teachSkills;
    private final Set<String> learnSkills;

    public Student(int id, String name,
                   Set<String> teachSkills,
                   Set<String> learnSkills) {
        this.id = id;
        this.name = name;
        this.teachSkills = new HashSet<>(teachSkills);
        this.learnSkills = new HashSet<>(learnSkills);
    }

    public int getId() {
        return id;
    }

    public String getName() {
        return name;
    }

    public Set<String> getTeachSkills() {
        return new HashSet<>(teachSkills);
    }

    public Set<String> getLearnSkills() {
        return new HashSet<>(learnSkills);
    }
}
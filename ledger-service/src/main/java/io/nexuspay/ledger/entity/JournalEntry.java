package ledger-service.io.nexuspay.ledger.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.time.Instant;
import java.util.UUID;

/**
 * Journal entry JPA entity
 */
@Data
@Entity
@Table(name = "journalentry")
public class JournalEntry {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false)
    private Instant createdAt = Instant.now();

    @Version
    private Long version;

}

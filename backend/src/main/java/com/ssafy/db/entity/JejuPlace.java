package com.ssafy.db.entity;

import com.sun.istack.NotNull;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import javax.persistence.*;

@Entity
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class JejuPlace {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private int id;
    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "category_id")
    private Category category;

    @Column(length = 150)
    private String name;
    private Double latitude;
    private Double longitude;
    private String roadAddress;
    private String placeUrl;
    private String imgUrl;
    private int reviewScoreSum;
    private int reviewCount;
    @Column(length = 150)
    private String tag;
}

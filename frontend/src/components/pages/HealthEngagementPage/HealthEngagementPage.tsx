/* External Dependencies */
import { useEffect, useState } from 'react';

/* Internal Dependencies */
// Services
import { fetchHealthData } from '../../../services/fetchHealthData';
// Utilities
import calculateProgress from './calculateProgress';
// Types
import type { HealthRecommendations, AnswerData } from '../../../types/HealthRecommendations';
import type { Progress } from '../../../types/Progress';
// Styles
import theme from '../../../styles/theme';
import { StyledHealthEngagementPage } from './HealthEngagementPage.styles';
// Components
import Header from '../../layout/Header';
import Footer from '../../layout/Footer';
import ScoreDial from '../../ui/ScoreDial/ScoreDial';
import CategoryListItem from '../../ui/CategoryListItem/CategoryListItem';


function HealthEngagementPage() {

    const [data, setData] = useState<HealthRecommendations | null>(null);
    const [progress, setProgress] = useState<Progress>({ overallProgress: 0, categoryProgress: {} } as Progress);

    useEffect(() => {
        const loadData = async () => {
            const healthData = await fetchHealthData();
            setData(healthData);
            setProgress(calculateProgress(healthData));
        };

        loadData();
    }, []);

    function updateActivity(categoryIndex: number, activityIndex: number, answers: AnswerData) {
        const newData = { ...data };
        let correct = 0;

        // Count how many "yes" answers
        Object.values(answers).forEach(answer => {
            if (answer === "yes") {
                correct += 1;
            }
        });

        // Get the original question count from the unmodified data
        const originalQuestionCount = data.categories[categoryIndex].activities[activityIndex].user_input_questions.length;

        // Remove the questions with "yes" answers (from highest index to lowest to avoid shifting problems)
        const indicesToRemove = Object.entries(answers)
            .filter(([_, answer]) => answer === "yes")
            .map(([index, _]) => Number(index))
            .sort((a, b) => b - a);

        indicesToRemove.forEach(index => {
            newData.categories[categoryIndex].activities[activityIndex].user_input_questions.splice(index, 1);
        });

        // Compare against the original question count in data, not newData
        if (correct >= originalQuestionCount) {
            newData.categories[categoryIndex].activities[activityIndex].status = "Completed";
        } else if (correct > 0) {
            newData.categories[categoryIndex].activities[activityIndex].status = "Partially completed";
        } else {
            newData.categories[categoryIndex].activities[activityIndex].status = "Not started";
        }

        setData(newData);
        setProgress(calculateProgress(newData));
    }



    if (!data) return <LoadingPlaceholder />;

    return (
        <StyledHealthEngagementPage>
            <Header />
            <div className="mainContent">
                <div className="scoreCard">
                    <ScoreDial score={progress.overallProgress} />
                    <div className="introText">
                        <h1><span className="highlight">Lisa's</span> Health Engagement Score</h1>
                        <p>Shows how you are tracking against established guidelines for health</p>
                    </div>
                </div>
                <div className="categoryList">
                    {data.categories.map((category, i) => (
                        <CategoryListItem
                            key={category.category_name}
                            categoryData={category}
                            categoryProgress={progress.categoryProgress[category.category_name]}
                            index={i}
                            color={theme.colors.categories[i % theme.colors.categories.length]}
                            updateActivity={updateActivity}
                        />
                    ))}
                </div>
            </div>
            <Footer />
        </StyledHealthEngagementPage>
    );
}


function LoadingPlaceholder() {
    return (
        <p>Loading...</p>
    )
}





export default HealthEngagementPage;
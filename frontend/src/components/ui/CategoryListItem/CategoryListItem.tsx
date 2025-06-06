/* External Dependencies */
import { useState } from 'react';
import AccordionDetails from '@mui/material/AccordionDetails';
import AccordionSummary from '@mui/material/AccordionSummary';
// Icons
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import HelpTwoToneIcon from '@mui/icons-material/HelpTwoTone';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';
import IncompleteCircleIcon from '@mui/icons-material/IncompleteCircle';

/* Internal Dependencies */
// Styles
import theme from '../../../styles/theme';
import StyledCategoryListItem, { StyledActivityListItem } from './CategoryListItem.styles';
// Types
import type { Category, ActivityItem, AnswerData } from '../../../types/HealthRecommendations';
import type { CategoryProgress } from '../../../types/Progress';
// Components
import ProgressBar from '../ProgressBar/ProgressBar';
import ActivityQuestionDialog from '../ActivityQuestionDialog/ActivityQuestionDialog';

export default function CategoryListItem({ categoryData, categoryProgress, color, index, updateActivity }: { categoryData: Category, categoryProgress: CategoryProgress, color: string, index: number, updateActivity: (categoryIndex: number, activityIndex: number, answers: AnswerData) => void }) {
    return (
        <StyledCategoryListItem className="categoryListItem" defaultExpanded={index === 0}>
            <AccordionSummary>
                <div className="categoryItemHeader">
                    <h2>{categoryData.category_name}</h2>
                    <p>{categoryProgress.progress}/{categoryProgress.totalActivities}</p>
                </div>
                <ProgressBar
                    variant="determinate" value={(categoryProgress.progress / categoryProgress.totalActivities) * 100}
                    barColor={color} />
            </AccordionSummary>
            <AccordionDetails>
                <div className="activityList">
                    {categoryData.activities.map((activityItem, activityIndex) => (
                        <ActivityListItem
                            key={activityItem.activity.recommendation_short_str}
                            activityItem={activityItem}
                            color={color}
                            categoryIndex={index}
                            activityIndex={activityIndex}
                            updateActivity={updateActivity}
                        />
                    ))}
                </div>
            </AccordionDetails>
        </StyledCategoryListItem>
    )
}


function ActivityListItem({ activityItem, color, categoryIndex, activityIndex, updateActivity }: { activityItem: ActivityItem, color: string, categoryIndex: number, activityIndex: number, updateActivity: (categoryIndex: number, activityIndex: number, answers: AnswerData) => void }) {

    const [dialogOpen, setDialogOpen] = useState(false);

    function openDialog() {
        console.log("open dialog")
        setDialogOpen(true);
    }

    function handleCloseDialog(answers: AnswerData | undefined) {
        console.log("close dialog")
        if (answers) {
            updateActivity(categoryIndex, activityIndex, answers);
        }
        setDialogOpen(false);
        console.log("Answers:", answers)
    }
    return (
        <StyledActivityListItem  >
            <div className="activityListItem" onClick={openDialog}>
                <div className="activityTextContainer">
                    <h3>{activityItem.activity.recommendation_short_str}</h3>
                    <h3 className="frequency">{activityItem.activity.frequency_short_str}</h3>
                </div>
                {
                    activityItem.status === "Completed" ?
                        <CheckCircleIcon className="statusIcon" id="completed" sx={{ color: color }} /> :
                        activityItem.status === "Not started" ?
                            <CancelOutlinedIcon className="statusIcon" id="notStarted" sx={{ color: theme.colors.text.quaternary }} /> :
                            activityItem.status === "Partially completed" ?
                                <IncompleteCircleIcon className="statusIcon" id="partial" sx={{ color: color }} /> :
                                <HelpTwoToneIcon className="statusIcon" id="needsConfirmation" sx={{
                                    color: color,
                                }} />
                }
            </div>
            <ActivityQuestionDialog activityData={activityItem} handleCloseDialog={handleCloseDialog} dialogOpen={dialogOpen} />
        </StyledActivityListItem>
    )
}


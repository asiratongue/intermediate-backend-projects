from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from Workouts.models import Workout_Plan
from rest_framework import status
from Progression.models import Scheduler
from .serializers import SchedulerObjSerializer
from .tasks import check_workout_started, check_workout_completed
from django.utils import timezone
from datetime import datetime, timedelta

  
class ScheduleWorkout(APIView):
    model = Scheduler
    permission_classes = [IsAuthenticated]

    def post(self, request, idx=None):

        user = request.user
        if "mark_as_pending" in request.data:
            try:
                sched_obj = Scheduler.objects.get(pk=request.data["mark_as_pending"])
                sched_obj.status = "PENDING"
                sched_obj.save()
                return Response({f"you have changed the status of your workout {sched_obj.workout} to {sched_obj.status}!": "woop woop!"}, status=status.HTTP_200_OK)
            
            except Scheduler.DoesNotExist:
                return Response({"error": "Scheduler object not found"}, status=status.HTTP_404_NOT_FOUND)
            

        if idx is None:
            return Response({"error": "Workout session ID required"}, status=status.HTTP_400_BAD_REQUEST)
        else:

            try:
                workout_plan = Workout_Plan.objects.get(pk=idx)
            except Workout_Plan.DoesNotExist:
                return Response({"error": "Couldn't find the workout session, get ids from workout/list/"}, status=status.HTTP_404_NOT_FOUND)

            if workout_plan.user != request.user:
                return Response({"error": "Wrong workout session id! get ids from workout/list/"}, status=status.HTTP_400_BAD_REQUEST)

            
            if "start_time" in request.data:
                data = {
                    "workout": workout_plan.id,
                    "start_time": request.data["start_time"],
                    "duration": request.data["duration"],
                    "user" : user.id
                }

                serializer = SchedulerObjSerializer(data=data)
                if not serializer.is_valid():
                    return Response({"error": serializer.errors}, 
                                status=status.HTTP_400_BAD_REQUEST)

                schedule_obj = serializer.save()
                now = timezone.now()
                start_time = schedule_obj.start_time
                completion_time = start_time + schedule_obj.duration


                if start_time <= now:
                    check_workout_started.apply_async(
                        args=[schedule_obj.id],
                        countdown=0
                    )
                else:
                    check_workout_started.apply_async(
                        args=[schedule_obj.id],
                        eta=start_time
                    )

                # Schedule completion task
                if completion_time <= now:
                    check_workout_completed.apply_async(
                        args=[schedule_obj.id],
                        countdown=0
                    )
                else:
                    check_workout_completed.apply_async(
                        args=[schedule_obj.id],
                        eta=completion_time
                    )

                return Response(
                    {"message" : f"Your task has been scheduled for {schedule_obj.start_time}"}, 
                    status=status.HTTP_201_CREATED
                )

            return Response(
                {"error": "you must schedule a workout or change its status!"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        


class DeleteScheduledWorkout(APIView):
    model = Scheduler
    permission_classes = [IsAuthenticated]

    def delete(self, request, idx = None):
        user = request.user
        if idx:

            try:
                SchedulerObj = Scheduler.objects.get(pk = idx)
                if SchedulerObj.user == user:
                    SchedulerObj.delete()
                    return Response({f"you have deleted the Scheduled Workout!, {SchedulerObj.workout} " : " woop woop!"})
                
            except Scheduler.DoesNotExist:
                return Response ({"error" : "this Scheduled Workout does not exist!, check your id number?"}, status=status.HTTP_404_NOT_FOUND)
            


class UpdateScheduledWorkout(APIView):
    model = Scheduler
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, idx = None):
        user = request.user
        
        if idx:
            try:

                if request.data["scheduled_workout"]:
                    ScheduledObj = Scheduler.objects.get(pk = idx)
                    

                    if ScheduledObj.user != user:
                        return Response("wrong Scheduled session id!, retrieve your ids from /schedule/list/!", status=status.HTTP_400_BAD_REQUEST)
                    
                    for key, value in request.data["scheduled_workout"].items():

                        if key == "start_time": 
                            ScheduledObj.start_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")  
                            continue
                        
                        elif key == "duration":
                            ScheduledObj.duration = timedelta(minutes=int(value))
                            
                    Workout2Update = Workout_Plan.objects.get(pk = request.data["scheduled_workout"]["workout_id"])
                    ScheduledObj.workout = Workout2Update
                    ScheduledObj.save()
                    return Response ({"Waheey you have sucessfully updated your scheduled workout!" : 
                                      f"new start time: {ScheduledObj.start_time}, new duration: {ScheduledObj.duration}, new workout plan: {ScheduledObj.workout.name}"})
                
            except Scheduler.DoesNotExist:
                    return Response ({"error" : "this Scheduled Workout does not exist!, check your id number?"}, status=status.HTTP_404_NOT_FOUND)



class Report(APIView):
    model = Scheduler
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        now = timezone.now()
        try:
            CurrentWorkouts = []
            CompletedWorkouts = []
            x, y = 0, 0
            AllSchedulerObjs = Scheduler.objects.filter(user = user.id)

            for SchedulerObj in AllSchedulerObjs:
                if SchedulerObj.start_time > now:
                    continue

                else:
                    CurrentWorkouts.append(SchedulerObj)

            for Objects in CurrentWorkouts:
                if Objects.status == 'PENDING':
                    x +=1
                elif Objects.status == 'COMPLETED':
                    CompletedWorkouts.append(Objects.workout.name)
                    y +=1
                else:
                    continue

            percentage = y/(x+y) * 100

            return Response ({f"hello {user.username}!" : f"you have a completion rate of {percentage}%!",
                              f"in the past year you have completed {y} workouts, well done!" : f" here are your completed workouts!:{CompletedWorkouts}"})

        except Scheduler.DoesNotExist:
            return Response ({"error" : "No Scheduled workouts were found"}, status=status.HTTP_404_NOT_FOUND)
            


class ListScheduledWorkouts(APIView):
    model = Scheduler
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        
        try:

            AllSchedulerObjs = Scheduler.objects.filter(user = user.id)
            SchedulerList = []
            StatusName = ""

            for Schedulerobj in AllSchedulerObjs:
                

                if request.data["List"] == "Pending":

                    if Schedulerobj.status == "PENDING":
                        SchedulerList.append(Schedulerobj)
                        StatusName = "Pending"

                if request.data["List"] == "Completed":

                    if Schedulerobj.status == "COMPLETED":
                        SchedulerList.append(Schedulerobj)
                        StatusName = "Completed"
                
                if request.data["List"] == "All":
                    return Response ({"Here are all Workouts within the Scheduler!" : f"""{[[scheduler_obj.workout.name, scheduler_obj.start_time, 
                                                                                            scheduler_obj.status, scheduler_obj.duration] for scheduler_obj in AllSchedulerObjs]}"""})
                
                else:
                    return Response({"error" : "Bad Request!, you must provide what to list by sending {'List' : 'All/Completed/Pending'}"}, status=status.HTTP_400_BAD_REQUEST)
                    
            return Response({f"here are all {StatusName} Workouts! " : f"{[[scheduler_obj.workout.name, scheduler_obj.start_time, 
                                                                            scheduler_obj.status, scheduler_obj.duration] 
                                                                           for scheduler_obj in SchedulerList]}"})  
        except Scheduler.DoesNotExist:
            return Response ({"error" : "No Scheduled workouts were found"}, status=status.HTTP_404_NOT_FOUND)


class QueryScheduledWorkouts(APIView):
    model = User
    permission_classes = [IsAuthenticated]

    def get(self, request):
        SchedulerDict = {}

        query_params = request.GET.keys()
        valid_params = {'date', 'workout'}

        date_query = request.GET.get('date')
        workout_query = request.GET.get('workout')

        invalid_params = set(query_params) - valid_params
        if invalid_params:
            return Response(
                {"error": f"Invalid query parameters: {', '.join(invalid_params)}. Valid parameters are: date, workout"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if date_query == None and workout_query == None:
            return Response ({"error" : "you must make a query!"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if date_query is None or workout_query:
                SearchResult = Scheduler.objects.filter(workout__id=workout_query)

                if not SearchResult:
                        return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)
                else:            
                    for Schedulerobj in SearchResult:
                        SchedulerDict[Schedulerobj.id] = {"start_time" : Schedulerobj.start_time,
                                                            "duration" : Schedulerobj.duration,
                                                            "status" : Schedulerobj.status}
                    return Response ({"Search Results from Workout query!" : SchedulerDict})#FORMAT THIS BETTER . . . 
            
            elif date_query:
                date_object = datetime.strptime(date_query, "%Y-%m-%d")
                dateQueryResult = Scheduler.objects.filter(start_time__gte=date_object)
                if not dateQueryResult:
                    return Response({"error" : "No Matches Found"}, status=status.HTTP_404_NOT_FOUND)
                else:
                    for Schedulerobj in dateQueryResult:
                        SchedulerDict[Schedulerobj.id] = {"start_time" : Schedulerobj.start_time,
                                                            "duration" : Schedulerobj.duration,
                                                            "status" : Schedulerobj.status}
                    return Response ({"Search Results from Workout query!" : SchedulerDict})#FORMAT THIS BETTER . . . 
  
        except Scheduler.DoesNotExist:
            return Response({"error": "No matches found"}, status=status.HTTP_404_NOT_FOUND)

# the above would make more sense in a function.
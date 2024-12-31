from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Workout_Plan, Exercise, Exercise_Session, Muscle_Group
from rest_framework import status
from .serializers import ExerciseSessionSerializer 
import json
from django.http import HttpResponse


class GetExercise(APIView):

    model = Exercise
    permission_classes = [IsAuthenticated]

    def get (self, request, id = None):
        if id:    
            try:
                FetchedExcercise = Exercise.objects.get(pk = id)

                return Response(f"""Name: {FetchedExcercise.name}, Description: {FetchedExcercise.description}, Category: {FetchedExcercise.category}, Muscle Groups: {[y.name for y in FetchedExcercise.MuscleGroup.all()]}""")
            
            except Exercise.DoesNotExist:
                return Response({"error!": "Exercise not found, check your key!"}, status=status.HTTP_404_NOT_FOUND)


class CreateWorkout(APIView):

    model = Workout_Plan
    permission_classes = [IsAuthenticated]
    
    def post (self, request):
        user = request.user

        try:
            if request.data.get("exercise_session") and request.data.get("workout_plan"):

                MyDict = self.Get_Exercise_Dict(request, user)
                if isinstance(MyDict, Response):
                    return(MyDict)
                
                else:
                    return self.create_workout_plan(request, user, MyDict)
            else:
                return Response ({"error!" : "invalid request data!"}, status=status.HTTP_400_BAD_REQUEST)
            
        except (Exercise_Session.DoesNotExist, Workout_Plan.DoesNotExist) as e:
            return Response(f"an object was not found: {e}", status=status.HTTP_404_NOT_FOUND)

    def Get_Exercise_Dict(self, request, user):
        exercise_session_dict = {}
        for key in request.data["exercise_session"]:
            if "exercise_session" in key:
                exercise_session_dict[key] = request.data["exercise_session"][key] 

            else:
                continue 
        
        for session_key, session_data in exercise_session_dict.items():

            if isinstance(session_data, int):
                break

            else:
                try:      
                    ExerciseObj = Exercise.objects.get(name=session_data["exercise"])
                except KeyError as e:
                    return Response(f"error: {e}", status=status.HTTP_400_BAD_REQUEST) 

                data={
                        "user": user.id,  
                        "exercise": ExerciseObj.id, 
                        "sets": session_data["sets"],  
                        "repetitions": session_data["repetitions"],  
                        "weights": session_data["weights"] 
                    }
            try:  
                Serializer = ExerciseSessionSerializer(data=data) 


                if Serializer.is_valid():
                    Serializer.save()

            except Serializer.errors as e:
                return Response (f"error: {e}", status=status.HTTP_400_BAD_REQUEST)
            
        return(exercise_session_dict)
                

    def create_workout_plan(self, request, user, MyDict):         

        for key in request.data["workout_plan"]:
            
            if key == "name" or key == "comments":
                continue

            WorkoutName = request.data["workout_plan"]["name"]
            WorkoutComments = request.data["workout_plan"]["comments"]

            workoutseshtuple = Workout_Plan.objects.get_or_create(user = user, name = WorkoutName, comments = WorkoutComments)
            workout_plan = workoutseshtuple[0]

            Keydata = request.data["workout_plan"][key]

            if isinstance(MyDict[Keydata], int):
                try:
                    ExerciseSession = Exercise_Session.objects.get(pk = MyDict[Keydata])
                except Exercise_Session.DoesNotExist as e:
                    return Response ({"error": f"{e}"}, status=status.HTTP_404_NOT_FOUND)
                workout_plan.Exercise_Session.add(ExerciseSession)
                workout_plan.save()

            else:
                exercise_x = MyDict[Keydata]["exercise"]
                exerciseID = Exercise.objects.get(name=exercise_x)
                ExerciseSessionID = Exercise_Session.objects.get(user = user, exercise = exerciseID, 
                                                                repetitions = MyDict[Keydata]["repetitions"], 
                                                                weights = MyDict[Keydata]["weights"] )                         
                                                                                                                                            
                workout_plan.Exercise_Session.add(ExerciseSessionID)                                                                          
                workout_plan.save()      
    
        all_exercise_sessions = workout_plan.Exercise_Session.all()

        return Response({f"hello {user.username}!, you have created a new workout session! (id: {workout_plan.id})" : f"""{workout_plan.name} {
            [["name: " + exercise_sesh.exercise.name, "sets: " + str(exercise_sesh.sets), "reps: " + str(exercise_sesh.repetitions), 
                "weights: " + str(exercise_sesh.weights), "Exercise Session ID: " + str(exercise_sesh.id)] 
            for exercise_sesh in all_exercise_sessions]}"""})


class RemoveWorkout(APIView):

    model = Workout_Plan
    permission_classes = [IsAuthenticated]

    def delete (self, request, id = None):
        user = request.user
        print("RemoveWorkout view called")
        if id:

            try:
                workout_plan = Workout_Plan.objects.get(pk = id)

                if workout_plan.user == user:
                    workout_plan.delete()
                    return Response ({f"message" : f"you have deleted the workout session '{workout_plan.name}' "})

                else:
                    return Response ("wrong workout session id!, retrieve your id's from workout/list/", status=status.HTTP_400_BAD_REQUEST)
                
            except Workout_Plan.DoesNotExist:
                return Response ({"error" : "this workout session does not exist!, check your id number?"}, status=status.HTTP_404_NOT_FOUND)


class UpdateWorkout(APIView):

    model = Workout_Plan
    permission_classes = [IsAuthenticated]

    def patch (self, request, id = None):
        user = request.user
        update_list = []

        if not id:
            return Response({"error!":"you gave no IDS!"}, status=status.HTTP_404_NOT_FOUND)

        try:
            if request.data.get("workout_plan"):
                return self.update_workout_plan(request, user, id)
            elif request.data.get("exercise_session"):
                return self.update_exercise_session(request, user, id)
            else:
                return Response ({"error" : "invalid request data!"}, status=status.HTTP_400_BAD_REQUEST)
 
        except (Exercise_Session.DoesNotExist, Workout_Plan.DoesNotExist) as e:
            return Response(f"an object was not found: {e}", status=status.HTTP_404_NOT_FOUND)
        
    def update_workout_plan(self, request, user, id):
        workout_plan = Workout_Plan.objects.get(pk = id) 
        update_list = []

        if workout_plan.user != user:
            return Response ("wrong workout session id!, retrieve your id's from workout/list/", status=status.HTTP_400_BAD_REQUEST)
        
        for keys in request.data["workout_plan"]:

            if keys == "name":
                workout_plan.name = request.data["workout_plan"][keys]
                workout_plan.save()
                continue
                
            update_list.append(request.data["workout_plan"][keys])

        workout_plan.Exercise_Session.set(update_list, clear=True)
        all_exercise_sessions2 = workout_plan.Exercise_Session.all()

        return Response ({"Message" : "You have sucessfully updated your workout!",
                            "New name" : f"{workout_plan.name}",
                            "New exercise sessions": f"{[xs.id for xs in all_exercise_sessions2]}"})



    def update_exercise_session(self, request, user, id): 
        GetExerciseSession = Exercise_Session.objects.get(pk = id)

        if GetExerciseSession.user != user:
            return Response ("wrong exercise session id!, retrieve your id's from url!", status=status.HTTP_400_BAD_REQUEST)
            
        else:
            GetExerciseSession.exercise = Exercise.objects.get(name = request.data["exercise_session"]["exercise"])
            GetExerciseSession.sets = request.data["exercise_session"]["sets"]
            GetExerciseSession.repetitions = request.data["exercise_session"]["repetitions"]
            GetExerciseSession.weights = request.data["exercise_session"]["weights"]
            GetExerciseSession.save()

            return Response({"message " : " You have successfully updated you exercise session!", 
                                "new changes ":{
                                "exercise": f"{GetExerciseSession.exercise.name}", 
                                "sets:" : f"{GetExerciseSession.sets}",
                                "repetitions:" : f"{GetExerciseSession.repetitions}", 
                                "weights:" : f"{GetExerciseSession.weights}" 

                            }})



def ListFunct(user, Obj):
    AllInstances = Obj.objects.filter(user = user.id)
    InstanceDict = {}

    for Instance in AllInstances:
        if isinstance(Instance, Exercise_Session):
            InstanceDict[Instance.exercise.name] = f"reps: {Instance.repetitions}, sets: {Instance.sets}, weights: {Instance.weights}"
        else:
            InstanceDict[Instance.name] = f"{Instance.comments}, Exercise Sessions: {[[x.exercise, x.repetitions, x.sets, x.weights] 
                                                                                                    for x in Instance.Exercise_Session.all()]}"              
    return InstanceDict


class ListWorkout(APIView):
    model = Workout_Plan
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
  
        try:
            WorkoutPlan = Workout_Plan
            WorkoutSessionDict = ListFunct(user, WorkoutPlan)

    
            return Response(WorkoutSessionDict)
        
        except Workout_Plan.DoesNotExist:
            return Response ({"ERROR":"couldnt find any matches"}, status=status.HTTP_404_NOT_FOUND)


class ListExerciseSessions(APIView):
    model = Exercise_Session
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        try:
            ExerciseSession = Exercise_Session
            ExerciseSessionDict = ListFunct(user, ExerciseSession)

            return Response(ExerciseSessionDict)
        
        except Exercise_Session.DoesNotExist:
            return Response ({"ERROR":"couldnt find any matches"}, status=status.HTTP_404_NOT_FOUND)


class ListExercises(APIView):
    model = Exercise
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            all_exercises = Exercise.objects.all()
            exercise_list = [
                {
                    "name": exercise.name,
                    "description": exercise.description,
                    "muscles_worked": [muscle.name for muscle in exercise.MuscleGroup.all()],
                    "id": exercise.id,
                }
                for exercise in all_exercises
            ]
            return Response(exercise_list, content_type="application/json")

        except Exercise.DoesNotExist:
            return Response ("ERROR", status=status.HTTP_404_NOT_FOUND)
